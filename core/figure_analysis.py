import base64
import json
import logging
from pathlib import Path

import fitz
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from core.arxiv_download import _download_pdf_bytes, PaperNotFoundError

logger = logging.getLogger(__name__)

# core/figure_analysis.py -> parent is core/, parent.parent is the project
# root, where papers/ lives. figures/ sits alongside raw/, parent/, child/
# as its own peer stage (see core/paper_chunking.py for the same pattern).
FIGURES_DIR = (Path(__file__).parent.parent / "papers" / "figures").resolve()

# Skips icons/logos/decorative images (arXiv PDFs commonly embed small
# rule lines, bullet glyphs, or watermark-sized images that aren't
# figures) — a real plot/diagram/photo is virtually always bigger than
# this on both axes.
MIN_FIGURE_DIMENSION = 150

# Safety cap, same spirit as arxiv_download.py's other _MAX_* limits: a
# long paper can embed dozens of images, and each one costs a full
# vision-model inference call — bound it rather than let one paper run
# unboundedly long.
MAX_FIGURES_PER_PAPER = 20

VISION_PROMPT = (
    "Describe this figure from an academic paper concisely but "
    "completely: what kind of figure it is (plot, diagram, architecture "
    "sketch, photo, table rendered as an image, etc.), what it shows, key "
    "labels or axes if visible, and the main takeaway if it's visually "
    "apparent. If the image isn't a real figure (e.g. a logo, watermark, "
    "or decorative element), say so briefly instead of inventing content."
)


def _figures_path(paper_id: str) -> Path:
    return FIGURES_DIR / f"{paper_id}.jsonl"


def _extract_figure_images(pdf_bytes: bytes) -> list[dict]:
    """Pulls embedded images out of a PDF's pages, skipping anything too
    small to plausibly be a real figure, capped at MAX_FIGURES_PER_PAPER.

    Returns [{"page": int, "image": bytes, "ext": str}, ...] in reading
    order (page order, then embedding order within a page).
    """

    figures = []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    try:
        for page_index, page in enumerate(doc):

            for img in page.get_images(full=True):

                xref = img[0]
                base_image = doc.extract_image(xref)

                if (
                    base_image.get("width", 0) < MIN_FIGURE_DIMENSION
                    or base_image.get("height", 0) < MIN_FIGURE_DIMENSION
                ):
                    continue

                figures.append({
                    "page": page_index,
                    "image": base_image["image"],
                    "ext": base_image["ext"]
                })

                if len(figures) >= MAX_FIGURES_PER_PAPER:
                    return figures
    finally:
        doc.close()

    return figures


def _describe_figure(vision_model: ChatOllama, image_bytes: bytes, ext: str) -> str:
    """Sends one figure to the vision model and returns its description.

    Standard LangChain multimodal message shape: a HumanMessage with a
    text block and an image_url block carrying a base64 data URL.
    ChatOllama parses the data URL itself (splits on the comma) and sends
    the payload as Ollama's own `images` field — no extra handling needed
    on our side.
    """

    encoded = base64.b64encode(image_bytes).decode("ascii")

    message = HumanMessage(content=[
        {"type": "text", "text": VISION_PROMPT},
        {"type": "image_url", "image_url": f"data:image/{ext};base64,{encoded}"}
    ])

    response = vision_model.invoke([message])

    return response.content if isinstance(response.content, str) else str(response.content)


def ensure_paper_figures(paper_id: str, vision_model_name: str) -> list[dict]:
    """Extracts and describes a paper's figures, or returns the cached
    result if this paper's figures were already analyzed.

    Idempotent like ensure_paper_chunks: writes papers/figures/<paper_id>.jsonl
    once (one JSON record per figure: paper_id, page, index, description),
    and any later call for the same paper_id just reads it back rather
    than re-running (real cost here: one vision-model inference call per
    figure).

    Unlike ensure_paper_chunks, this always does its own PDF fetch —
    arXiv's LaTeX/HTML sources aren't what's needed here (figures live in
    the rendered PDF), so this can't reuse whatever download_paper already
    fetched for the paper's text, regardless of which format that was.
    """

    path = _figures_path(paper_id)

    if path.exists():
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    pdf_bytes = _download_pdf_bytes(paper_id)
    figures = _extract_figure_images(pdf_bytes)

    # reasoning=False: verified live against a real reasoning-capable model
    # (qwen3.5) that this matters, not just theoretical — for a complex
    # figure, the default (model decides) let it spend its entire output
    # budget "thinking" internally and hit the token limit before ever
    # writing the actual description: no exception raised, just a
    # successful call with empty content (response_metadata's
    # done_reason was "length", not "stop" — easy to miss, looks like a
    # clean success otherwise). A figure caption doesn't need extended
    # reasoning anyway; this is a no-op for vision models that don't
    # support the toggle at all.
    vision_model = ChatOllama(model=vision_model_name, temperature=0, reasoning=False)

    records = []

    for index, figure in enumerate(figures):
        try:
            description = _describe_figure(vision_model, figure["image"], figure["ext"])
        except Exception:
            logger.exception("Vision model failed to describe figure %d of %s", index, paper_id)
            description = "(description unavailable — the vision model failed on this figure)"

        records.append({
            "paper_id": paper_id,
            "page": figure["page"],
            "index": index,
            "description": description
        })

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    return records


def make_analyze_paper_figures_tool(vision_model_name: str):
    """
    Builds the `analyze_paper_figures` tool bound to whichever
    vision-capable Ollama model was auto-detected for this session. Only
    added to the agent's tools at all when such a model exists — see
    graph.py — so the tool's mere presence already signals the
    capability; no "vision model unavailable" branch needed inside it.
    """

    @tool
    def analyze_paper_figures(paper_id: str) -> str:
        """
        Extracts and describes the figures, diagrams, and charts embedded
        in a paper's PDF, using a local vision-capable model — this is
        the only way to learn what a figure actually shows; none of the
        text-based tools (read_paper, search_paper_content) can see
        images. The paper must already have been downloaded with
        download_paper (any paper_id works, regardless of which format
        download_paper used for its text — this always fetches the PDF
        rendition separately, since figures live there).

        Slow (one vision-model call per figure) and results are a
        model-generated interpretation, not verified fact — cite them
        accordingly (e.g. "Figure 2 appears to show...").
        """

        try:
            records = ensure_paper_figures(paper_id, vision_model_name)
        except PaperNotFoundError as exc:
            return json.dumps({"status": "error", "message": str(exc)})
        except Exception as exc:
            return json.dumps({"status": "error", "message": f"Error: {exc}"})

        if not records:
            return json.dumps({
                "status": "success",
                "paper_id": paper_id,
                "message": "No figures found (or none large enough to be worth describing).",
                "figures": []
            })

        return json.dumps({
            "status": "success",
            "paper_id": paper_id,
            "figures": records
        })

    return analyze_paper_figures
