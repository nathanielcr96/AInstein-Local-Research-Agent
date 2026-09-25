<!-- entry:000001:start -->
## [000001] research_topic — 2026-09-09T17:04:54
User is starting to study attention mechanisms in transformers and wants to understand efficient fine-tuning techniques like LoRA and QLoRA.
<!-- entry:000001:end -->
<!-- entry:000002:start -->
## [000002] paper — 2026-09-10T12:36:10
arXiv ID: 2604.00965
Title: Understanding Transformers and Attention Mechanisms: An Introduction for Applied Mathematicians
Authors: Michel Fabrice Serret
Categories: math.NA
Published: 2026-04-01T14:39:28Z
Local file: papers/raw/2604.00965.md (full text retrieved)
Abstract: This document provides a brief introduction to the attention mechanism used in modern language models based on the Transformer architecture. We first illustrate how text is encoded as vectors and how the attention mechanism processes these vectors to encode semantic information. We then describe Multi-Headed Attention, examine how the Transformer architecture is built and look at some of its variants. Finally, we provide a glimpse at modern methods to reduce the computational and memory cost of attention, namely KV caching, Grouped Query attention and Latent Attention. This material is aimed at the applied mathematics community and was written as introductory presentation in the context of the IPAM Research Collaboration Workshop entitled "Randomized Numerical Linear Algebra" (RNLA), for the project: "Randomization in Transformer models".
<!-- entry:000002:end -->
<!-- entry:000003:start -->
## [000003] paper — 2026-09-11T14:13:03
arXiv ID: 1706.03762
Title: Attention Is All You Need
Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
Categories: cs.CL, cs.LG
Published: 2017-06-12T17:57:34Z
Local file: papers/raw/1706.03762.md (full text retrieved)
Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.
<!-- entry:000003:end -->
<!-- entry:000004:start -->
## [000004] paper — 2026-09-10T17:01:18
arXiv ID: 2106.09685
Title: LoRA: Low-Rank Adaptation of Large Language Models
Authors: Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen
Categories: cs.CL, cs.AI, cs.LG
Published: 2021-06-17T17:37:18Z
Local file: papers/raw/2106.09685.md (full text retrieved)
Abstract: An important paradigm of natural language processing consists of large-scale pre-training on general domain data and adaptation to particular tasks or domains. As we pre-train larger models, full fine-tuning, which retrains all model parameters, becomes less feasible. Using GPT-3 175B as an example -- deploying independent instances of fine-tuned models, each with 175B parameters, is prohibitively expensive. We propose Low-Rank Adaptation, or LoRA, which freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks. Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times. LoRA performs on-par or better than fine-tuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3, despite having fewer trainable parameters, a higher training throughput, and, unlike adapters, no additional inference latency. We also provide an empirical investigation into rank-deficiency in language model adaptation, which sheds light on the efficacy of LoRA. We release a package that facilitates the integration of LoRA with PyTorch models and provide our implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at https://github.com/microsoft/LoRA.
<!-- entry:000004:end -->
<!-- entry:000005:start -->
## [000005] paper — 2026-09-14T13:17:00
arXiv ID: 2305.14314
Title: QLoRA: Efficient Finetuning of Quantized LLMs
Authors: Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer
Categories: cs.LG
Published: 2023-05-23T00:00:00Z
Local file: papers/raw/2305.14314.md (full text retrieved)
Abstract: We present QLoRA, an efficient finetuning approach that reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance. QLoRA backpropagates gradients through a frozen, 4-bit quantized pretrained language model into Low Rank Adapters (LoRA). Our best model family, which we name Guanaco, outperforms all previous openly released models on the Vicuna benchmark, reaching 99.3% of the performance level of ChatGPT while only requiring 24 hours of finetuning on a single GPU. QLoRA introduces a number of innovations to save memory without sacrificing performance: (a) 4-bit NormalFloat (NF4), a new data type that is information theoretically optimal for normally distributed weights (b) Double Quantization to reduce the average memory footprint by quantizing the quantization constants, and (c) Paged Optimizers to manage memory spikes.
<!-- entry:000005:end -->
<!-- entry:000006:start -->
## [000006] keyword — 2026-09-13T12:47:47
parameter-efficient fine-tuning (PEFT) — a broad category of techniques for adapting pre-trained models with limited compute, including but not limited to LoRA and QLoRA.
<!-- entry:000006:end -->
<!-- entry:000007:start -->
## [000007] preference — 2026-09-13T13:16:41
Always give intuition before formulas when explaining technical concepts. Never present formulas first without prior intuitive explanation.
<!-- entry:000007:end -->
<!-- entry:000008:start -->
## [000008] paper — 2026-09-17T08:23:32
arXiv ID: 2609.16661
Title: DiaWhisper-DPO: Role-Attributed Transcription of Clinical Interviews via Failure-Mined Preference Optimization
Authors: Weiming Li, Ana Catarina Fidalgo Barata, Miguel Constante, João Miguel Sanches
Categories: cs.CL
Published: 2026-09-15T05:32:27+00:00
Local file: papers/raw/2609.16661.md (full text retrieved)
Abstract: Automated depression screening from clinical interviews requires attribution of utterances to the clinician or patient. We evaluate two datasets: DAIC-WOZ, where participant-only recordings require re-synthesizing both sides for controlled two-party evaluation, and PDCH-HAMD, comprising voice-converted real Chinese interviews for cross-lingual validation. Cascaded systems combine speaker diarization with role-assignment heuristics, so errors can propagate across stages. We propose an end-to-end model, which we named DiaWhisper, that fine-tunes Whisper-large-v3 with LoRA and an auxiliary frame-level role head for transcription and attribution, together with DiaWhisper-DPO, a failure-mined refinement that uses genuine decoding failures as DPO rejected completions without human preference annotation. On 29 DAIC-WOZ test sessions, DiaWhisper-DPO achieves 0.973 role accuracy and 0.119 DER, 72% below the strongest cascaded baseline, and reduces seed variation from σ = .205 to .002. Retrained on PDCH-HAMD, it achieves 0.757 role accuracy and improves all 78 session-seed pairs.
<!-- entry:000008:end -->
<!-- entry:000009:start -->
## [000009] paper — 2026-09-17T08:23:34
arXiv ID: 2609.16644
Title: WholeBodyWAM: Generalizing Pre-trained World-Action Priors to Humanoid Loco-Manipulation via WBC-Grounded Coordination
Authors: Zhuo Li, Yiming Yao, Jim Tan, Mengjie Jing, Zhipeng Dong, Fei Chen
Categories: cs.RO
Published: 2026-09-15T05:03:49+00:00
Local file: papers/raw/2609.16644.md (full text retrieved)
Abstract: World Action Models (WAMs) offer a promising approach to general-purpose robot manipulation by jointly modeling visual dynamics and actions. However, most WAM studies focus on tabletop or arm-centric manipulation, while humanoid loco-manipulation remains less explored. To address this gap, we introduce WholeBodyWAM, which jointly predicts future visual dynamics, manipulation actions, and whole-body control intents for generalizable humanoid loco-manipulation. It preserves pre-trained world-action priors while grounding heterogeneous whole-body controller (WBC) semantics and coordinating whole-body behavior. Extensive experiments show that WholeBodyWAM achieves an overall simulation task success rate of 91.9%, with a 0.23 improvement in real-world out-of-distribution task progress and a 70% reduction in success-rate variance across WBCs relative to the respective baselines. These results suggest a path toward scalable humanoid whole-body intelligence by extending pre-trained world-action priors through structured WBC grounding and coordination, rather than relearning whole-body behavior from scratch. Project page: https://wholebodywam.github.io/.
<!-- entry:000009:end -->
<!-- entry:000010:start -->
## [000010] paper — 2026-09-17T08:23:38
arXiv ID: 2609.16604
Title: ExecuCritic: Calibrated Critic Shaping for Code Generation with Verifiable Rewards
Authors: Junjie Cao, Yingjie He
Categories: cs.SE
Published: 2026-09-15T03:58:21+00:00
Local file: papers/raw/2609.16604.md (full text retrieved)
Abstract: Execution feedback is a useful supervision signal for code models because unit tests are objective and directly measure program correctness. Its weakness is that an entire program is often reduced to one pass or fail bit, leaving RLVR to solve a difficult credit assignment problem. At the same time, coding systems often include separate reviewer or tester roles, but these critics are usually prompted rather than trained and are not calibrated against execution. We propose ExecuCritic, a joint training framework in which a coder and a critic are updated on the same execution rollouts. The critic predicts pass or fail outcomes and gives short diagnostic feedback; the coder uses this signal only when the critic agrees with the executor on the current rollout group. Across eight code benchmarks and two recent open backbones, ExecuCritic improves over GRPO without a critic, prompted reviewer systems and scalar reward model baselines, while requiring fewer policy gradient steps and fewer sandbox executions. Ablations and reliability analyses suggest that the gains come from better credit assignment rather than larger sampling budgets.
<!-- entry:000010:end -->
<!-- entry:000011:start -->
## [000011] paper — 2026-09-17T08:23:41
arXiv ID: 2609.16737
Title: Visual Cue Guided Video Planning for Generalizable Robot Navigation
Authors: Hojin Lee, Sizhe Lester Li, Maximilian Hilger, Susie Lu, Achim J. Lilienthal, Vincent Sitzmann, Daniel A. Duecker
Categories: cs.RO, cs.AI, cs.CV, cs.LG
Published: 2026-09-15T07:11:21+00:00
Local file: papers/raw/2609.16737.md (full text retrieved)
Abstract: Generative video models can serve as a promising backbone for robot navigation by predicting future observations as video plans. Recent approaches often condition video planning on short-horizon guidance and recover geometric waypoints through scene reconstruction, leaving longer-horizon planning and precise video-to-action translation less explored. We present CueNav, a video model-based navigation framework combining visual cue guided video planning with an embodiment-specific Inverse-Dynamics Model (IDM). As visual cues, we use a Bird's-Eye View (BEV) map to convey global task context and retain part of the robot body in the egocentric observation to expose embodiment context. These cues guide the video planner, while the IDM translates dense flow fields extracted from the video plan into robot actions. With the visual cue encoding global task context, CueNav achieves nearly 2x higher success in maze navigation than planning without the cue. The body-aware view with the IDM enables precise navigation with 70% success in a narrow passage where comparison methods largely fail to complete the task. We further demonstrate zero-shot semantic-conditioned navigation and deployment of the same video planner across different robot platforms. Our results show that visual cue-guided video planning with embodiment-specific action grounding paves the way toward a generalizable navigation framework for longer-horizon planning and embodiment-aware control. Additional results and code are available on our project website: https://cuenav.github.io.
<!-- entry:000011:end -->
<!-- entry:000012:start -->
## [000012] paper — 2026-09-17T08:23:50
arXiv ID: 2609.16486
Title: VPRef: A Cross-Domain Benchmark for Referring Remote Sensing Image Segmentation
Authors: Quanwei Liu, Tao Huang, Jiaqi Yang, Wei Xiang
Categories: cs.CV
Published: 2026-09-15T01:18:06+00:00
Local file: papers/raw/2609.16486.md (full text retrieved)
Abstract: Rapid advancements in vision-language models have propelled Referring Remote Sensing Image Segmentation (RRSIS) to the forefront of Earth observation. However, practical deployments suffer severe performance degradation under a coupled dual-drift paradigm: visual domain drift from cross-spatial-resolution mismatches and spectral variations, alongside textual logic drift from unconstrained, variable user-input granularities. To mitigate these bottlenecks, this paper establishes the first cross-domain RRSIS benchmark, designated as the Vaihingen-Potsdam Referring (VPRef) dataset, comprising 46,972 language-image-annotation triplets organized into a three-tier linguistic hierarchy. Building upon this benchmark, we develop a tailored parameter-efficient domain adaptation baseline anchored on the Segment Anything Model (SAM3) via Low-Rank Adaptation (LoRA). Our framework counteracts visual distribution discrepancies through pseudo-label-driven self-training and addresses textual logic drift via random multi-granularity text prompt mixing. Crucially, the distribution of empirical metrics across ablative variants suggests a potential decoupling between cross-modal semantic robustification and visual domain alignment, demonstrating that linguistic variance drives fine-grained semantic invariance while pseudo-label propagation governs macro-scale spatial grid alignment. Extensive benchmarks demonstrate the proposed framework achieves superior cross-domain segmentation boundaries while modifying merely 1.08\% of the foundational parameter footprint, establishing a robust baseline for future multi-modal remote sensing domain adaptation research. The dataset and code will be available at https://github.com/quanweiliu/VPRef.
<!-- entry:000012:end -->
<!-- entry:000013:start -->
## [000013] paper — 2026-09-17T08:23:53
arXiv ID: 2609.16537
Title: What Does Layer-Importance Reveal About Transformers and State-Space Models?
Authors: Istabrak Abbes, Nizar Islah, Irina Rish, Sarath Chandar
Categories: cs.LG, cs.AI
Published: 2026-09-15T02:34:13+00:00
Local file: papers/raw/2609.16537.md (full text retrieved)
Abstract: Transformers and state-space models (SSMs) are the two dominant families of sequence models, and a central open question is how far the analytical knowledge built for transformers transfers to SSMs. We address this through the lens of layer importance which underpins compression, selective fine-tuning, and interpretability across both families. We decompose layer importance into two distinct notions. \emph{Necessity} captures how much the pretrained model depends on a layer's existing contribution, measured by the loss increase from bypassing it. \emph{Plasticity} captures where the model absorbs new information during fine-tuning, measured by the magnitude of task-specific weight updates. Our analysis reveals that the two families behave fundamentally differently: in every evaluated residual transformer up to $14$B parameters, Necessity and Plasticity anti-align across depth, whereas in the evaluated Mamba-style SSMs they point to overlapping regions. The sign of this alignment also predicts downstream adaptation behavior. In the evaluated transformers, concentrating updates in the most plastic layers increases catastrophic forgetting, while this tier-dependent effect disappears in the evaluated Mamba-style SSMs.
<!-- entry:000013:end -->
<!-- entry:000014:start -->
## [000014] paper — 2026-09-17T08:24:09
arXiv ID: 2609.16664
Title: Bridging the Perceptual Gap: Residual-Enhanced Downscaling and Manifold-Aware Perception Alignment Adaptation for NR-IQA
Authors: Yu Li, Zhengran Shen, Yachun Mi, Puchao Zhou, Shaohui Liu
Categories: cs.CV
Published: 2026-09-15T05:38:56+00:00
Local file: papers/raw/2609.16664.md (full text retrieved)
Abstract: Leveraging Large Vision-Language Models like CLIP has recently set new benchmarks for No-Reference Image Quality Assessment (NR-IQA). However, the contrastive pretraining of CLIP inherently prioritizes semantic invariance, which often suppresses subtle perceptual signals, a phenomenon we term perceptual submergence. Furthermore, standard preprocessing techniques (e.g., cropping and interpolation) further exacerbate the loss of critical high-frequency quality cues. In this paper, we propose the Cross-modal Perception Alignment Adapter (CMPA), a manifold-aware framework designed to disentangle perceptual distortions from dominant semantics. CMPA introduces a Perception-Sensitive Feature Extractor (PFE) that projects CLIP features into a compact, low-dimensional subspace, explicitly magnifying distortion-induced off-manifold deviations. Subsequently, a Cross-Modal Perception Alignment Injector (PAI) aligns these features with quality-aware text anchors and re-injects them into the backbone. To ensure input fidelity, we also devise a Residual-enhanced Perceptual Downscaling strategy that adaptively compensates for resolution-induced information loss using Just Noticeable Difference (JND) guided frequency re-injection. Extensive evaluations on several benchmark datasets demonstrate that our approach significantly outperforms state-of-the-art methods, effectively recovering the perceptual signals submerged in semantic-dense representations.
<!-- entry:000014:end -->
<!-- entry:000015:start -->
## [000015] paper — 2026-09-17T08:24:11
arXiv ID: 2609.16601
Title: SAVOR: Self-Aware Visual Grounding via Confidence-Calibrated Reinforcement Learning for Multimodal Hallucination Mitigation
Authors: Zixiu Ding, Zilin Zhao, Yingjie He, Xinlang Kang, Guansu Wang, Wei Zhang
Categories: cs.CV
Published: 2026-09-15T03:53:32+00:00
Local file: papers/raw/2609.16601.md (full text retrieved)
Abstract: Multimodal large language models (MLLMs) have made strong progress on visual question answering and image captioning, yet they still produce fluent claims about objects, attributes, or relations that are not grounded in the image. Many remedies either modify decoding at test time, which adds latency, or fine tune with preferences such as DPO variants, which teach which answer is preferred but not when the model's own answer is unreliable. We argue that calibrated self assessment is the missing signal. We introduce Savor, a training framework that (i) augments the output schema with token and answer confidence, (ii) optimises the policy with a Group Relative Policy Optimisation (GRPO) objective that penalises calibration error and poor abstention decisions, and (iii) uses the learned confidence at inference time to revisit visual evidence only when the model is uncertain. Experiments on POPE, HallusionBench, AMBER and MMHal-Bench across two recent backbones (InternVL3-8B and Qwen3-VL-8B) show that Savor reduces hallucination while preserving general capability on MME and MMBench, with lower Expected Calibration Error than DPO and decoding baselines.
<!-- entry:000015:end -->
<!-- entry:000016:start -->
## [000016] paper — 2026-09-17T08:24:15
arXiv ID: 2609.16875
Title: Multi-modal Knowledge Preserving Adapter for Embedding Backward Compatibility
Authors: Jaeseok Byun, Gukyeong Kwon, Han-Kai Hsu, Meher Gitika Karumuri, Zhikang Zhang, Hao Yang, Davide Modolo
Categories: cs.CV
Published: 2026-09-15T09:06:00+00:00
Local file: papers/raw/2609.16875.md (full text retrieved)
Abstract: Upgrading embedding models typically requires expensive database re-indexing, as new query embeddings are incompatible with existing database embeddings. While Backward Compatible Training (BCT) mitigates this by enforcing compatibility during training, existing approaches often require updating the backbone model. This is impractical because of significant training cost, the risk of performance regression, and limited access to proprietary model weights. We introduce Multi-modal Knowledge Preserving Adapter (MKP-Adapter), the first adapter-only BCT approach for Multi-modal Large Language Models (MLLMs) that requires no backbone updates. We identified that the primary challenge in adapter-only BCT is preserving the knowledge of the new embeddings while enforcing backward compatibility. Hence, we propose a multi-level preservation loss that maintains the geometric structure of the embedding spaces throughout BCT. Furthermore, a focal re-weighting strategy is integrated to prioritize learning from challenging samples. Experiments demonstrate that our method achieves strong backward compatibility across diverse multi-modal benchmarks (image, text, visual document, and video retrieval tasks) and model types. Notably, MKP-Adapter is trained solely on pre-extracted embeddings and requires only negligible additional latency relative to the original backbone forward pass, highlighting its efficiency.
<!-- entry:000016:end -->
<!-- entry:000017:start -->
## [000017] paper — 2026-09-17T08:24:17
arXiv ID: 2609.17021
Title: sensVLA: Spatially-Grounded Vision-Language-Action Model for Autonomous Wheel Loader
Authors: Gopi Krishna Erabati, Bjarne Johannsen, Angus Stewart, Vardeep Singh Sandhu
Categories: cs.CV, cs.RO
Published: 2026-09-15T11:29:50+00:00
Local file: papers/raw/2609.17021.md (full text retrieved)
Abstract: Autonomous wheel-loader control requires joint reasoning over task semantics, egocentric vision, proprioception, and 3D scene geometry. We present sensVLA, a Vision-Language-Action (VLA) architecture that combines a Qwen3-2B Vision-Language Model (VLM) with a fully trainable transformer action expert trained by flow-matching velocity regression. sensVLA routes Bird's-Eye-View (BEV) features, extracted from fused front and rear lidar, directly to the action expert through a dedicated cross-attention pathway, while the VLM consumes front and rear RGB views to provide task-conditioned semantic context. This design decouples spatial grounding from linguistic reasoning while preserving interaction between both streams at decision time. The expert predicts six action dimensions: longitudinal velocity, steering, body-frame displacement, arm rate, and bucket rate. On a real-world dataset from a wheel loader, sensVLA reaches aggregate per-step parity with a strong camera-only baseline and reduces longitudinal velocity RMSE by 28% and displacement error by 9% on loading centric scenarios. It also degrades 29% less when the camera stream is corrupted or removed, evidencing that explicit spatial grounding improves accuracy and fault-tolerance for heavy equipment autonomy.
<!-- entry:000017:end -->
<!-- entry:000018:start -->
## [000018] paper — 2026-09-17T08:24:21
arXiv ID: 2609.17019
Title: SKIP: a Self-knowledge-guided Step-wise Preference Learning Framework for Concise Reasoning
Authors: Qinhong Lin, Yuhao Zhang, Yinglun Feng, Zhongliang Yang, Linna Zhou
Categories: cs.AI
Published: 2026-09-15T11:29:29+00:00
Local file: papers/raw/2609.17019.md (full text retrieved)
Abstract: While Chain-of-Thought (CoT) reasoning has been proven to be effective, it often leads to overthinking, resulting in computational overhead, inference latency, and even degraded performance in large language models (LLMs). Existing concise reasoning frameworks significantly compromise accuracy while compressing the length of output. In this paper, we propose SKIP, a self-knowledge-guided step-wise preference learning framework. Starting with lightweight fine-tuning to adjust the model's output style, SKIP introduces a carefully designed knowledge probing mechanism to guide model to output an answer at each reasoning step. Based on the correctness of intermediate steps, we construct preference data that guide the model toward more efficient and correct reasoning by leveraging DPO. Experimental results demonstrate that our method effectively improves reasoning compression while mitigating performance degradation after fine-tuning. Besides, SKIP shows strong generalization ability on out-of-distribution datasets. We further conducted ablation studies on the component parameters of our framework.
<!-- entry:000018:end -->
<!-- entry:000019:start -->
## [000019] paper — 2026-09-17T08:24:24
arXiv ID: 2609.17109
Title: Shared-Prefix KV Reuse Across Standard LoRA Adapters: Quality and Serving Tradeoffs
Authors: Dushyant Rajput
Categories: cs.AI, cs.CL
Published: 2026-09-15T12:39:16+00:00
Local file: papers/raw/2609.17109.md (full text retrieved)
Abstract: A common small-model deployment runs one shared backbone with several LoRA specialists that answer over the same context. Serving them naively re-prefills that shared context once per specialist. We study a narrow, practical question: for already-trained standard LoRA adapters -- not adapters retrained for cache compatibility -- how much task quality is preserved if the backbone's prefill KV cache is computed once and reused across specialists, and what does that buy in serving cost? On a Qwen3-1.7B backbone with two adapters (extractive QA on HotpotQA, arithmetic reasoning on GSM8K), we sweep the boundary at which the specialist takes over from the reused base cache and measure paired quality differences and serving cost. Full-prefix reuse had the lowest prefill cost and a small quality difference on held-out GSM8K (Delta = -4.6 EM at a 160-token budget; -3.0 at 320 tokens; -0.8 under a second training seed -- all favoring native, only the first excluding zero, and the magnitude not consistent). Partial recomputation provided no demonstrated advantage. Neither quality equivalence nor a general boundary-selection rule is established. We also report a closed-form ridge KV translator that did not beat direct reuse, and specialist-dependence contrasts whose intervals all include zero. The measured serving benefit is warm-cache time-to-first-token, which grows with context (~16x at 8K); two-branch peak memory was only 12% lower and, on inspection, the prefix was never physically shared across branches -- this implementation reuses KV values but copies their storage, so shared-cache memory savings are not achieved.
<!-- entry:000019:end -->
<!-- entry:000020:start -->
## [000020] paper — 2026-09-17T08:24:27
arXiv ID: 2609.17234
Title: Self-Distilled Pronunciation and Accent Control for Neural Text-to-Speech
Authors: Shuhei Kato
Categories: cs.SD, eess.AS
Published: 2026-09-15T14:13:51+00:00
Local file: papers/raw/2609.17234.md (full text retrieved)
Abstract: Text-to-speech that reads raw text has no lexicon: a rare word is read as guessed. Remedies train a reading-and-accent channel on recorded speech or edit words one at a time from exemplars. We do neither. The frozen backbone reads a sentence containing a common word it already says correctly, and its own output then serves as the teacher for the same sentence, with that word replaced by a tagged, accented reading; this training pair is the whole idea. On Sarashina2.2-TTS, screened raters at Fleiss' kappa = 0.85 hear the prescribed accent on 0.89 of unseen words against 0.57 for kana, which cannot express one; kana wins no pair; naturalness is not measurably hurt. Moved untuned to autoregressive, diffusion, and encoder-decoder backbones, it transfers reading, 0.25 to 0.47 above no edit on 319 words, and on CosyVoice 2 accent on two words in three, but not on Irodori; the paper locates why.
<!-- entry:000020:end -->
<!-- entry:000021:start -->
## [000021] paper — 2026-09-17T08:24:30
arXiv ID: 2609.17398
Title: Enhancing Accessibility of Medical Texts through Large Language Model-Driven Plain Language Adaptation
Authors: Ting-Wei Chang, Hen-Hsen Huang, Hsin-Hsi Chen
Categories: cs.CL
Published: 2026-09-15T16:33:38+00:00
Local file: papers/raw/2609.17398.md (full text retrieved)
Abstract: This paper addresses the challenge of making complex healthcare information more accessible through automated Plain Language Adaptation (PLA). PLA aims to simplify technical medical language, bridging a critical gap between the complexity of healthcare texts and patients' reading comprehension. Recent advances in Large Language Models (LLMs), such as GPT and BART, have opened new possibilities for PLA, especially in zero-shot and few-shot learning contexts where task-specific data is limited. In this work, we leverage the capabilities of LLMs such as GPT-4o-mini, Gemini-1.5-pro, and LLaMA for text simplification. Additionally, we incorporate Mixture-of-Agents (MoA) techniques to enhance adaptability and robustness in PLA tasks. Key contributions include a comparative analysis of prompting strategies, finetuning with QLoRA on different LLMs, and the integration of MoA technique. Our findings demonstrate the effectiveness of LLM-driven PLA, showcasing its potential in making healthcare information more comprehensible while preserving essential content.
<!-- entry:000021:end -->
<!-- entry:000022:start -->
## [000022] paper — 2026-09-17T08:24:34
arXiv ID: 2609.15177
Title: Temporal Self-Distillation: Faster Inference in Discrete Diffusion Language Models
Authors: Shijian Xu, Andrea Miele, Metod Jazbec, Volker Roth, Eric Nalisnick, Ilija Bogunovic
Categories: cs.LG
Published: 2026-09-14T07:59:45+00:00
Local file: papers/raw/2609.15177.md (full text retrieved)
Abstract: Diffusion language models (dLLMs) promise fast inference by generating multiple tokens in parallel, but suffer severe performance degradation when parallel decoding is pushed too aggressively. We introduce Temporal Self-Distillation (TSD), a simple on-policy method that trains dLLMs for fast inference by distilling predictions across time. Specifically, TSD distills the model's denoising distribution at earlier timesteps toward its distribution at the final timestep at which a token is committed. This encourages earlier predictions to better anticipate the model's eventual output, enabling much more aggressive parallel decoding. Because its teacher signal comes from the model itself, TSD requires no offline teacher generation and applies seamlessly to both base and post-trained policies. Across seven benchmarks in mathematics, planning, and code, TSD substantially shifts the speed--quality frontier toward the low-compute regime. TSD thus provides a simple, single-stage approach to accelerating dLLMs, achieving speedups competitive with offline distillation while avoiding a complex two-stage pipeline.
<!-- entry:000022:end -->
<!-- entry:000023:start -->
## [000023] paper — 2026-09-17T08:36:58
arXiv ID: 2505.09388
Title: Qwen3 Technical Report
Authors: An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Gao, Chengen Huang, Chenxu Lv, Chujie Zheng, Dayiheng Liu, Fan Zhou, Fei Huang, Feng Hu, Hao Ge, Haoran Wei, Huan Lin, Jialong Tang, Jian Yang, Jianhong Tu, Jianwei Zhang, Jianxin Yang, Jiaxi Yang, Jing Zhou, Jingren Zhou, Junyang Lin, Kai Dang, Keqin Bao, Kexin Yang, Le Yu, Lianghao Deng, Mei Li, Mingfeng Xue, Mingze Li, Pei Zhang, Peng Wang, Qin Zhu, Rui Men, Ruize Gao, Shixuan Liu, Shuang Luo, Tianhao Li, Tianyi Tang, Wenbiao Yin, Xingzhang Ren, Xinyu Wang, Xinyu Zhang, Xuancheng Ren, Yang Fan, Yang Su, Yichang Zhang, Yinger Zhang, Yu Wan, Yuqiong Liu, Zekun Wang, Zeyu Cui, Zhenru Zhang, Zhipeng Zhou, Zihan Qiu
Categories: cs.CL
Published: 2025-05-14T13:41:34+00:00
Local file: papers/raw/2505.09388.md (full text retrieved)
Abstract: In this work, we present Qwen3, the latest version of the Qwen model family. Qwen3 comprises a series of large language models (LLMs) designed to advance performance, efficiency, and multilingual capabilities. The Qwen3 series includes models of both dense and Mixture-of-Expert (MoE) architectures, with parameter scales ranging from 0.6 to 235 billion. A key innovation in Qwen3 is the integration of thinking mode (for complex, multi-step reasoning) and non-thinking mode (for rapid, context-driven responses) into a unified framework. This eliminates the need to switch between different models--such as chat-optimized models (e.g., GPT-4o) and dedicated reasoning models (e.g., QwQ-32B)--and enables dynamic mode switching based on user queries or chat templates. Meanwhile, Qwen3 introduces a thinking budget mechanism, allowing users to allocate computational resources adaptively during inference, thereby balancing latency and performance based on task complexity. Moreover, by leveraging the knowledge from the flagship models, we significantly reduce the computational resources required to build smaller-scale models, while ensuring their highly competitive performance. Empirical evaluations demonstrate that Qwen3 achieves state-of-the-art results across diverse benchmarks, including tasks in code generation, mathematical reasoning, agent tasks, etc., competitive against larger MoE models and proprietary models. Compared to its predecessor Qwen2.5, Qwen3 expands multilingual support from 29 to 119 languages and dialects, enhancing global accessibility through improved cross-lingual understanding and generation capabilities. To facilitate reproducibility and community-driven research and development, all Qwen3 models are publicly accessible under Apache 2.0.
<!-- entry:000023:end -->
<!-- entry:000024:start -->
## [000024] paper — 2026-09-17T08:37:01
arXiv ID: 2006.11190
Title: Solving optimization problems with Rydberg analog quantum computers: Realistic requirements for quantum advantage using noisy simulation and classical benchmarks
Authors: Michel Fabrice Serret, Bertrand Marchand, Thomas Ayral
Categories: quant-ph, cond-mat.quant-gas
Published: 2020-06-19T15:42:24+00:00
Local file: papers/raw/2006.11190.md (full text retrieved)
Abstract: Platforms of Rydberg atoms have been proposed as promising candidates to solve some combinatorial optimization problems. Here, we compute quantitative requirements on the system sizes and noise levels that these platforms must fulfill to reach quantum advantage in approximately solving the Unit-Disk Maximum Independent Set problem. Using noisy simulations of Rydberg platforms of up to 26 atoms interacting through realistic van der Waals interactions, we compute the average approximation ratio that can be attained with a simple quantum annealing-based heuristic within a fixed temporal computational budget. Based on estimates of the correlation lengths measured in the engineered quantum state, we extrapolate the results to large atom numbers and compare them to a simple classical approximation heuristic. We find that approximation ratios of at least $\approx 0.84$ are within reach for near-future noise levels. Not taking into account further classical and quantum algorithmic improvements, we estimate that quantum advantage could be reached by attaining a number of controlled atoms of $\sim8,000$ for a time budget of 2 seconds, and $\sim 1,000-1,200$ for a time budget of 0.2 seconds, provided the coherence levels of the system can be improved by a factor 10 while maintaining a constant repetition rate.
<!-- entry:000024:end -->
<!-- entry:000025:start -->
## [000025] paper — 2026-09-17T08:37:05
arXiv ID: 1802.05751
Title: Image Transformer
Authors: Niki Parmar, Ashish Vaswani, Jakob Uszkoreit, Łukasz Kaiser, Noam Shazeer, Alexander Ku, Dustin Tran
Categories: cs.CV
Published: 2018-02-15T20:37:15+00:00
Local file: papers/raw/1802.05751.md (full text retrieved)
Abstract: Image generation has been successfully cast as an autoregressive sequence generation or transformation problem. Recent work has shown that self-attention is an effective way of modeling textual sequences. In this work, we generalize a recently proposed model architecture based on self-attention, the Transformer, to a sequence modeling formulation of image generation with a tractable likelihood. By restricting the self-attention mechanism to attend to local neighborhoods we significantly increase the size of images the model can process in practice, despite maintaining significantly larger receptive fields per layer than typical convolutional neural networks. While conceptually simple, our generative models significantly outperform the current state of the art in image generation on ImageNet, improving the best published negative log-likelihood on ImageNet from 3.83 to 3.77. We also present results on image super-resolution with a large magnification ratio, applying an encoder-decoder configuration of our architecture. In a human evaluation study, we find that images generated by our super-resolution model fool human observers three times more often than the previous state of the art.
<!-- entry:000025:end -->
<!-- entry:000026:start -->
## [000026] paper — 2026-09-17T08:37:07
arXiv ID: 1701.06538
Title: Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer
Authors: Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton, Jeff Dean
Categories: cs.LG, cs.CL, cs.NE, stat.ML
Published: 2017-01-23T18:10:00+00:00
Local file: papers/raw/1701.06538.md (full text retrieved)
Abstract: The capacity of a neural network to absorb information is limited by its number of parameters. Conditional computation, where parts of the network are active on a per-example basis, has been proposed in theory as a way of dramatically increasing model capacity without a proportional increase in computation. In practice, however, there are significant algorithmic and performance challenges. In this work, we address these challenges and finally realize the promise of conditional computation, achieving greater than 1000x improvements in model capacity with only minor losses in computational efficiency on modern GPU clusters. We introduce a Sparsely-Gated Mixture-of-Experts layer (MoE), consisting of up to thousands of feed-forward sub-networks. A trainable gating network determines a sparse combination of these experts to use for each example. We apply the MoE to the tasks of language modeling and machine translation, where model capacity is critical for absorbing the vast quantities of knowledge available in the training corpora. We present model architectures in which a MoE with up to 137 billion parameters is applied convolutionally between stacked LSTM layers. On large language modeling and machine translation benchmarks, these models achieve significantly better results than state-of-the-art at lower computational cost.
<!-- entry:000026:end -->
<!-- entry:000027:start -->
## [000027] paper — 2026-09-17T08:37:11
arXiv ID: 1906.05909
Title: Stand-Alone Self-Attention in Vision Models
Authors: Prajit Ramachandran, Niki Parmar, Ashish Vaswani, Irwan Bello, Anselm Levskaya, Jonathon Shlens
Categories: cs.CV
Published: 2019-06-13T19:43:01+00:00
Local file: papers/raw/1906.05909.md (full text retrieved)
Abstract: Convolutions are a fundamental building block of modern computer vision systems. Recent approaches have argued for going beyond convolutions in order to capture long-range dependencies. These efforts focus on augmenting convolutional models with content-based interactions, such as self-attention and non-local means, to achieve gains on a number of vision tasks. The natural question that arises is whether attention can be a stand-alone primitive for vision models instead of serving as just an augmentation on top of convolutions. In developing and testing a pure self-attention vision model, we verify that self-attention can indeed be an effective stand-alone layer. A simple procedure of replacing all instances of spatial convolutions with a form of self-attention applied to ResNet model produces a fully self-attentional model that outperforms the baseline on ImageNet classification with 12% fewer FLOPS and 29% fewer parameters. On COCO object detection, a pure self-attention model matches the mAP of a baseline RetinaNet while having 39% fewer FLOPS and 34% fewer parameters. Detailed ablation studies demonstrate that self-attention is especially impactful when used in later layers. These results establish that stand-alone self-attention is an important addition to the vision practitioner's toolbox.
<!-- entry:000027:end -->
<!-- entry:000028:start -->
## [000028] paper — 2026-09-17T08:37:29
arXiv ID: 2010.10648
Title: Towards End-to-End In-Image Neural Machine Translation
Authors: Elman Mansimov, Mitchell Stern, Mia Chen, Orhan Firat, Jakob Uszkoreit, Puneet Jain
Categories: cs.CL, cs.CV, cs.LG
Published: 2020-10-20T22:20:04+00:00
Local file: papers/raw/2010.10648.md (full text retrieved)
Abstract: In this paper, we offer a preliminary investigation into the task of in-image machine translation: transforming an image containing text in one language into an image containing the same text in another language. We propose an end-to-end neural model for this task inspired by recent approaches to neural machine translation, and demonstrate promising initial results based purely on pixel-level supervision. We then offer a quantitative and qualitative evaluation of our system outputs and discuss some common failure modes. Finally, we conclude with directions for future work.
<!-- entry:000028:end -->
<!-- entry:000029:start -->
## [000029] paper — 2026-09-17T08:37:35
arXiv ID: 2210.05666
Title: Point Transformer V2: Grouped Vector Attention and Partition-based Pooling
Authors: Xiaoyang Wu, Yixing Lao, Li Jiang, Xihui Liu, Hengshuang Zhao
Categories: cs.CV
Published: 2022-10-11T17:58:03+00:00
Local file: papers/raw/2210.05666.md (full text retrieved)
Abstract: As a pioneering work exploring transformer architecture for 3D point cloud understanding, Point Transformer achieves impressive results on multiple highly competitive benchmarks. In this work, we analyze the limitations of the Point Transformer and propose our powerful and efficient Point Transformer V2 model with novel designs that overcome the limitations of previous work. In particular, we first propose group vector attention, which is more effective than the previous version of vector attention. Inheriting the advantages of both learnable weight encoding and multi-head attention, we present a highly effective implementation of grouped vector attention with a novel grouped weight encoding layer. We also strengthen the position information for attention by an additional position encoding multiplier. Furthermore, we design novel and lightweight partition-based pooling methods which enable better spatial alignment and more efficient sampling. Extensive experiments show that our model achieves better performance than its predecessor and achieves state-of-the-art on several challenging 3D point cloud understanding benchmarks, including 3D point cloud segmentation on ScanNet v2 and S3DIS and 3D point cloud classification on ModelNet40. Our code will be available at https://github.com/Gofinge/PointTransformerV2.
<!-- entry:000029:end -->
<!-- entry:000030:start -->
## [000030] paper — 2026-09-17T08:37:38
arXiv ID: 2409.14842
Title: HW-TSC's Submission to the CCMT 2024 Machine Translation Tasks
Authors: Zhanglin Wu, Yuanchang Luo, Daimeng Wei, Jiawei Zheng, Bin Wei, Zongyao Li, Hengchao Shang, Jiaxin Guo, Shaojun Li, Weidong Zhang, Ning Xie, Hao Yang
Categories: cs.AI, cs.CL
Published: 2024-09-23T09:20:19+00:00
Local file: papers/raw/2409.14842.md (full text retrieved)
Abstract: This paper presents the submission of Huawei Translation Services Center (HW-TSC) to machine translation tasks of the 20th China Conference on Machine Translation (CCMT 2024). We participate in the bilingual machine translation task and multi-domain machine translation task. For these two translation tasks, we use training strategies such as regularized dropout, bidirectional training, data diversification, forward translation, back translation, alternated training, curriculum learning, and transductive ensemble learning to train neural machine translation (NMT) models based on the deep Transformer-big architecture. Furthermore, to explore whether large language model (LLM) can help improve the translation quality of NMT systems, we use supervised fine-tuning to train llama2-13b as an Automatic post-editing (APE) model to improve the translation results of the NMT model on the multi-domain machine translation task. By using these plyometric strategies, our submission achieves a competitive result in the final evaluation.
<!-- entry:000030:end -->
<!-- entry:000031:start -->
## [000031] paper — 2026-09-17T08:37:41
arXiv ID: 1707.04499
Title: LIUM Machine Translation Systems for WMT17 News Translation Task
Authors: Mercedes García-Martínez, Ozan Caglayan, Walid Aransa, Adrien Bardet, Fethi Bougares, Loïc Barrault
Categories: cs.CL
Published: 2017-07-14T13:10:22+00:00
Local file: papers/raw/1707.04499.md (full text retrieved)
Abstract: This paper describes LIUM submissions to WMT17 News Translation Task for English-German, English-Turkish, English-Czech and English-Latvian language pairs. We train BPE-based attentive Neural Machine Translation systems with and without factored outputs using the open source nmtpy framework. Competitive scores were obtained by ensembling various systems and exploiting the availability of target monolingual corpora for back-translation. The impact of back-translation quantity and quality is also analyzed for English-Turkish where our post-deadline submission surpassed the best entry by +1.6 BLEU.
<!-- entry:000031:end -->
<!-- entry:000032:start -->
## [000032] paper — 2026-09-17T08:37:44
arXiv ID: 2502.07864
Title: TransMLA: Multi-Head Latent Attention Is All You Need
Authors: Fanxu Meng, Pingzhi Tang, Xiaojuan Tang, Zengwei Yao, Xing Sun, Muhan Zhang
Categories: cs.LG, cs.AI
Published: 2025-02-11T18:20:18+00:00
Local file: papers/raw/2502.07864.md (full text retrieved)
Abstract: In this paper, we present TransMLA, a framework that seamlessly converts any GQA-based pre-trained model into an MLA-based model. Our approach enables direct compatibility with DeepSeek's codebase, allowing these models to fully leverage DeepSeek-specific optimizations such as vLLM and SGlang. By compressing 93% of the KV cache in LLaMA-2-7B, TransMLA achieves a 10.6x inference speedup at an 8K context length while preserving meaningful output quality. Additionally, the model requires only 6 billion tokens for fine-tuning to regain performance on par with the original across multiple benchmarks. TransMLA offers a practical solution for migrating GQA-based models to the MLA structure. When combined with DeepSeek's advanced features, such as FP8 quantization and Multi-Token Prediction, even greater inference acceleration can be realized.
<!-- entry:000032:end -->
<!-- entry:000033:start -->
## [000033] paper — 2026-09-17T08:37:48
arXiv ID: 2604.01757
Title: Attention Mechanisms Through the Lens of Numerical Methods: Approximation Methods and Alternative Formulations
Authors: Michel Fabrice Serret, Alice Cortinovis, Yijun Dong, Diana Halikias, Anna Ma, Fabio Matti, Deanna Needell, Katherine J. Pearce, Elizaveta Rebrova, Disha Shur, Rudi Smith, Hai-Xiao Wang, Laura Grigori
Categories: math.NA
Published: 2026-04-02T08:24:49+00:00
Local file: papers/raw/2604.01757.md (full text retrieved)
Abstract: The attention mechanism is the computational core of modern Transformer architectures, but its quadratic complexity in the input sequence length is the bottleneck for large-scale inference. This has motivated a rapidly growing body of work aimed at accelerating attention through approximation and reformulation. In this survey, we revisit attention mechanisms through the lens of numerical analysis, with a particular emphasis on tools and perspectives from numerical linear algebra. Our goal is twofold: first, we aim to systematically review and classify fast approximation methods according to the numerical principles they exploit. These include sparsity and clustering approaches, low-rank and subspace projection techniques, randomized sketching methods, and tensor-based decompositions. We also discuss kernel-inspired reformulations of attention and recent architectural variants, such as Latent Attention, that modify the standard softmax formulation to improve efficiency. Second, by presenting these developments within a unified mathematical framework, we aim to bridge the gap between disciplines and highlight opportunities for further contributions from computational mathematics, particularly numerical linear algebra, to the design of scalable attention mechanisms.
<!-- entry:000033:end -->
<!-- entry:000034:start -->
## [000034] paper — 2026-09-17T08:37:53
arXiv ID: 1806.01261
Title: Relational inductive biases, deep learning, and graph networks
Authors: Peter W. Battaglia, Jessica B. Hamrick, Victor Bapst, Alvaro Sanchez-Gonzalez, Vinicius Zambaldi, Mateusz Malinowski, Andrea Tacchetti, David Raposo, Adam Santoro, Ryan Faulkner, Caglar Gulcehre, Francis Song, Andrew Ballard, Justin Gilmer, George Dahl, Ashish Vaswani, Kelsey Allen, Charles Nash, Victoria Langston, Chris Dyer, Nicolas Heess, Daan Wierstra, Pushmeet Kohli, Matt Botvinick, Oriol Vinyals, Yujia Li, Razvan Pascanu
Categories: cs.LG, cs.AI, stat.ML
Published: 2018-06-04T17:58:18+00:00
Local file: papers/raw/1806.01261.md (full text retrieved)
Abstract: Artificial intelligence (AI) has undergone a renaissance recently, making major progress in key domains such as vision, language, control, and decision-making. This has been due, in part, to cheap data and cheap compute resources, which have fit the natural strengths of deep learning. However, many defining characteristics of human intelligence, which developed under much different pressures, remain out of reach for current approaches. In particular, generalizing beyond one's experiences--a hallmark of human intelligence from infancy--remains a formidable challenge for modern AI.   The following is part position paper, part review, and part unification. We argue that combinatorial generalization must be a top priority for AI to achieve human-like abilities, and that structured representations and computations are key to realizing this objective. Just as biology uses nature and nurture cooperatively, we reject the false choice between "hand-engineering" and "end-to-end" learning, and instead advocate for an approach which benefits from their complementary strengths. We explore how using relational inductive biases within deep learning architectures can facilitate learning about entities, relations, and rules for composing them. We present a new building block for the AI toolkit with a strong relational inductive bias--the graph network--which generalizes and extends various approaches for neural networks that operate on graphs, and provides a straightforward interface for manipulating structured knowledge and producing structured behaviors. We discuss how graph networks can support relational reasoning and combinatorial generalization, laying the foundation for more sophisticated, interpretable, and flexible patterns of reasoning. As a companion to this paper, we have released an open-source software library for building graph networks, with demonstrations of how to use them in practice.
<!-- entry:000034:end -->
<!-- entry:000035:start -->
## [000035] paper — 2026-09-17T08:37:56
arXiv ID: 1911.02150
Title: Fast Transformer Decoding: One Write-Head is All You Need
Authors: Noam Shazeer
Categories: cs.NE, cs.CL, cs.LG
Published: 2019-11-06T00:19:05+00:00
Local file: papers/raw/1911.02150.md (full text retrieved)
Abstract: Multi-head attention layers, as used in the Transformer neural sequence model, are a powerful alternative to RNNs for moving information across and between sequences. While training these layers is generally fast and simple, due to parallelizability across the length of the sequence, incremental inference (where such paralleization is impossible) is often slow, due to the memory-bandwidth cost of repeatedly loading the large "keys" and "values" tensors. We propose a variant called multi-query attention, where the keys and values are shared across all of the different attention "heads", greatly reducing the size of these tensors and hence the memory bandwidth requirements of incremental decoding. We verify experimentally that the resulting models can indeed be much faster to decode, and incur only minor quality degradation from the baseline.
<!-- entry:000035:end -->
<!-- entry:000036:start -->
## [000036] paper — 2026-09-17T08:37:59
arXiv ID: 2103.12731
Title: Scaling Local Self-Attention for Parameter Efficient Visual Backbones
Authors: Ashish Vaswani, Prajit Ramachandran, Aravind Srinivas, Niki Parmar, Blake Hechtman, Jonathon Shlens
Categories: cs.CV
Published: 2021-03-23T17:56:06+00:00
Local file: papers/raw/2103.12731.md (full text retrieved)
Abstract: Self-attention has the promise of improving computer vision systems due to parameter-independent scaling of receptive fields and content-dependent interactions, in contrast to parameter-dependent scaling and content-independent interactions of convolutions. Self-attention models have recently been shown to have encouraging improvements on accuracy-parameter trade-offs compared to baseline convolutional models such as ResNet-50. In this work, we aim to develop self-attention models that can outperform not just the canonical baseline models, but even the high-performing convolutional models. We propose two extensions to self-attention that, in conjunction with a more efficient implementation of self-attention, improve the speed, memory usage, and accuracy of these models. We leverage these improvements to develop a new self-attention model family, HaloNets, which reach state-of-the-art accuracies on the parameter-limited setting of the ImageNet classification benchmark. In preliminary transfer learning experiments, we find that HaloNet models outperform much larger models and have better inference performance. On harder tasks such as object detection and instance segmentation, our simple local self-attention and convolutional hybrids show improvements over very strong baselines. These results mark another step in demonstrating the efficacy of self-attention models on settings traditionally dominated by convolutional models.
<!-- entry:000036:end -->
<!-- entry:000037:start -->
## [000037] paper — 2026-09-17T08:38:02
arXiv ID: 1809.04281
Title: Music Transformer
Authors: Cheng-Zhi Anna Huang, Ashish Vaswani, Jakob Uszkoreit, Noam Shazeer, Ian Simon, Curtis Hawthorne, Andrew M. Dai, Matthew D. Hoffman, Monica Dinculescu, Douglas Eck
Categories: cs.LG, cs.SD, eess.AS, stat.ML
Published: 2018-09-12T07:15:26+00:00
Local file: papers/raw/1809.04281.md (full text retrieved)
Abstract: Music relies heavily on repetition to build structure and meaning. Self-reference occurs on multiple timescales, from motifs to phrases to reusing of entire sections of music, such as in pieces with ABA structure. The Transformer (Vaswani et al., 2017), a sequence model based on self-attention, has achieved compelling results in many generation tasks that require maintaining long-range coherence. This suggests that self-attention might also be well-suited to modeling music. In musical composition and performance, however, relative timing is critically important. Existing approaches for representing relative positional information in the Transformer modulate attention based on pairwise distance (Shaw et al., 2018). This is impractical for long sequences such as musical compositions since their memory complexity for intermediate relative information is quadratic in the sequence length. We propose an algorithm that reduces their intermediate memory requirement to linear in the sequence length. This enables us to demonstrate that a Transformer with our modified relative attention mechanism can generate minute-long compositions (thousands of steps, four times the length modeled in Oore et al., 2018) with compelling structure, generate continuations that coherently elaborate on a given motif, and in a seq2seq setup generate accompaniments conditioned on melodies. We evaluate the Transformer with our relative attention mechanism on two datasets, JSB Chorales and Piano-e-Competition, and obtain state-of-the-art results on the latter.
<!-- entry:000037:end -->
<!-- entry:000038:start -->
## [000038] paper — 2026-09-17T08:47:02
arXiv ID: 1705.04304
Title: A Deep Reinforced Model for Abstractive Summarization
Authors: Romain Paulus, Caiming Xiong, Richard Socher
Categories: cs.CL
Published: 2017-05-11T17:39:35+00:00
Local file: papers/raw/1705.04304.md (full text retrieved)
Abstract: Attentional, RNN-based encoder-decoder models for abstractive summarization have achieved good performance on short input and output sequences. For longer documents and summaries however these models often include repetitive and incoherent phrases. We introduce a neural network model with a novel intra-attention that attends over the input and continuously generated output separately, and a new training method that combines standard supervised word prediction and reinforcement learning (RL). Models trained only with supervised learning often exhibit "exposure bias" - they assume ground truth is provided at each step during training. However, when standard word prediction is combined with the global sequence prediction training of RL the resulting summaries become more readable. We evaluate this model on the CNN/Daily Mail and New York Times datasets. Our model obtains a 41.16 ROUGE-1 score on the CNN/Daily Mail dataset, an improvement over previous state-of-the-art models. Human evaluation also shows that our model produces higher quality summaries.
<!-- entry:000038:end -->
<!-- entry:000039:start -->
## [000039] paper — 2026-09-17T08:47:05
arXiv ID: 2403.11430
Title: A Novel Paradigm Boosting Translation Capabilities of Large Language Models
Authors: Jiaxin Guo, Hao Yang, Zongyao Li, Daimeng Wei, Hengchao Shang, Xiaoyu Chen
Categories: cs.CL
Published: 2024-03-18T02:53:49+00:00
Local file: papers/raw/2403.11430.md (full text retrieved)
Abstract: This paper presents a study on strategies to enhance the translation capabilities of large language models (LLMs) in the context of machine translation (MT) tasks. The paper proposes a novel paradigm consisting of three stages: Secondary Pre-training using Extensive Monolingual Data, Continual Pre-training with Interlinear Text Format Documents, and Leveraging Source-Language Consistent Instruction for Supervised Fine-Tuning. Previous research on LLMs focused on various strategies for supervised fine-tuning (SFT), but their effectiveness has been limited. While traditional machine translation approaches rely on vast amounts of parallel bilingual data, our paradigm highlights the importance of using smaller sets of high-quality bilingual data. We argue that the focus should be on augmenting LLMs' cross-lingual alignment abilities during pre-training rather than solely relying on extensive bilingual data during SFT. Experimental results conducted using the Llama2 model, particularly on Chinese-Llama2 after monolingual augmentation, demonstrate the improved translation capabilities of LLMs. A significant contribution of our approach lies in Stage2: Continual Pre-training with Interlinear Text Format Documents, which requires less than 1B training data, making our method highly efficient. Additionally, in Stage3, we observed that setting instructions consistent with the source language benefits the supervised fine-tuning process. Experimental results demonstrate that our approach surpasses previous work and achieves superior performance compared to models such as NLLB-54B and GPT3.5-text-davinci-003, despite having a significantly smaller parameter count of only 7B or 13B. This achievement establishes our method as a pioneering strategy in the field of machine translation.
<!-- entry:000039:end -->
<!-- entry:000040:start -->
## [000040] paper — 2026-09-17T08:47:15
arXiv ID: 1806.01830
Title: Relational Deep Reinforcement Learning
Authors: Vinicius Zambaldi, David Raposo, Adam Santoro, Victor Bapst, Yujia Li, Igor Babuschkin, Karl Tuyls, David Reichert, Timothy Lillicrap, Edward Lockhart, Murray Shanahan, Victoria Langston, Razvan Pascanu, Matthew Botvinick, Oriol Vinyals, Peter Battaglia
Categories: cs.LG, stat.ML
Published: 2018-06-05T17:39:12+00:00
Local file: papers/raw/1806.01830.md (full text retrieved)
Abstract: We introduce an approach for deep reinforcement learning (RL) that improves upon the efficiency, generalization capacity, and interpretability of conventional approaches through structured perception and relational reasoning. It uses self-attention to iteratively reason about the relations between entities in a scene and to guide a model-free policy. Our results show that in a novel navigation and planning task called Box-World, our agent finds interpretable solutions that improve upon baselines in terms of sample complexity, ability to generalize to more complex scenes than experienced during training, and overall performance. In the StarCraft II Learning Environment, our agent achieves state-of-the-art performance on six mini-games -- surpassing human grandmaster performance on four. By considering architectural inductive biases, our work opens new directions for overcoming important, but stubborn, challenges in deep RL.
<!-- entry:000040:end -->
<!-- entry:000041:start -->
## [000041] paper — 2026-09-17T08:47:18
arXiv ID: 2102.08602
Title: LambdaNetworks: Modeling Long-Range Interactions Without Attention
Authors: Irwan Bello
Categories: cs.CV, cs.LG
Published: 2021-02-17T06:33:47+00:00
Local file: papers/raw/2102.08602.md (full text retrieved)
Abstract: We present lambda layers -- an alternative framework to self-attention -- for capturing long-range interactions between an input and structured contextual information (e.g. a pixel surrounded by other pixels). Lambda layers capture such interactions by transforming available contexts into linear functions, termed lambdas, and applying these linear functions to each input separately. Similar to linear attention, lambda layers bypass expensive attention maps, but in contrast, they model both content and position-based interactions which enables their application to large structured inputs such as images. The resulting neural network architectures, LambdaNetworks, significantly outperform their convolutional and attentional counterparts on ImageNet classification, COCO object detection and COCO instance segmentation, while being more computationally efficient. Additionally, we design LambdaResNets, a family of hybrid architectures across different scales, that considerably improves the speed-accuracy tradeoff of image classification models. LambdaResNets reach excellent accuracies on ImageNet while being 3.2 - 4.4x faster than the popular EfficientNets on modern machine learning accelerators. When training with an additional 130M pseudo-labeled images, LambdaResNets achieve up to a 9.5x speed-up over the corresponding EfficientNet checkpoints.
<!-- entry:000041:end -->
<!-- entry:000042:start -->
## [000042] paper — 2026-09-17T08:47:26
arXiv ID: 2101.11605
Title: Bottleneck Transformers for Visual Recognition
Authors: Aravind Srinivas, Tsung-Yi Lin, Niki Parmar, Jonathon Shlens, Pieter Abbeel, Ashish Vaswani
Categories: cs.CV, cs.AI, cs.LG
Published: 2021-01-27T18:55:27+00:00
Local file: papers/raw/2101.11605.md (full text retrieved)
Abstract: We present BoTNet, a conceptually simple yet powerful backbone architecture that incorporates self-attention for multiple computer vision tasks including image classification, object detection and instance segmentation. By just replacing the spatial convolutions with global self-attention in the final three bottleneck blocks of a ResNet and no other changes, our approach improves upon the baselines significantly on instance segmentation and object detection while also reducing the parameters, with minimal overhead in latency. Through the design of BoTNet, we also point out how ResNet bottleneck blocks with self-attention can be viewed as Transformer blocks. Without any bells and whistles, BoTNet achieves 44.4% Mask AP and 49.7% Box AP on the COCO Instance Segmentation benchmark using the Mask R-CNN framework; surpassing the previous best published single model and single scale results of ResNeSt evaluated on the COCO validation set. Finally, we present a simple adaptation of the BoTNet design for image classification, resulting in models that achieve a strong performance of 84.7% top-1 accuracy on the ImageNet benchmark while being up to 1.64x faster in compute time than the popular EfficientNet models on TPU-v3 hardware. We hope our simple and effective approach will serve as a strong baseline for future research in self-attention models for vision
<!-- entry:000042:end -->
<!-- entry:000043:start -->
## [000043] paper — 2026-09-17T08:47:28
arXiv ID: 1906.01604
Title: KERMIT: Generative Insertion-Based Modeling for Sequences
Authors: William Chan, Nikita Kitaev, Kelvin Guu, Mitchell Stern, Jakob Uszkoreit
Categories: cs.CL, cs.LG, stat.ML
Published: 2019-06-04T17:35:35+00:00
Local file: papers/raw/1906.01604.md (full text retrieved)
Abstract: We present KERMIT, a simple insertion-based approach to generative modeling for sequences and sequence pairs. KERMIT models the joint distribution and its decompositions (i.e., marginals and conditionals) using a single neural network and, unlike much prior work, does not rely on a prespecified factorization of the data distribution. During training, one can feed KERMIT paired data $(x, y)$ to learn the joint distribution $p(x, y)$, and optionally mix in unpaired data $x$ or $y$ to refine the marginals $p(x)$ or $p(y)$. During inference, we have access to the conditionals $p(x \mid y)$ and $p(y \mid x)$ in both directions. We can also sample from the joint distribution or the marginals. The model supports both serial fully autoregressive decoding and parallel partially autoregressive decoding, with the latter exhibiting an empirically logarithmic runtime. We demonstrate through experiments in machine translation, representation learning, and zero-shot cloze question answering that our unified approach is capable of matching or exceeding the performance of dedicated state-of-the-art systems across a wide range of tasks without the need for problem-specific architectural adaptation.
<!-- entry:000043:end -->
<!-- entry:000044:start -->
## [000044] paper — 2026-09-17T08:47:32
arXiv ID: 1611.02683
Title: Unsupervised Pretraining for Sequence to Sequence Learning
Authors: Prajit Ramachandran, Peter J. Liu, Quoc V. Le
Categories: cs.CL, cs.LG, cs.NE
Published: 2016-11-08T20:42:26+00:00
Local file: papers/raw/1611.02683.md (full text retrieved)
Abstract: This work presents a general unsupervised learning method to improve the accuracy of sequence to sequence (seq2seq) models. In our method, the weights of the encoder and decoder of a seq2seq model are initialized with the pretrained weights of two language models and then fine-tuned with labeled data. We apply this method to challenging benchmarks in machine translation and abstractive summarization and find that it significantly improves the subsequent supervised models. Our main result is that pretraining improves the generalization of seq2seq models. We achieve state-of-the art results on the WMT English$\rightarrow$German task, surpassing a range of methods using both phrase-based machine translation and neural machine translation. Our method achieves a significant improvement of 1.3 BLEU from the previous best models on both WMT'14 and WMT'15 English$\rightarrow$German. We also conduct human evaluations on abstractive summarization and find that our method outperforms a purely supervised learning baseline in a statistically significant manner.
<!-- entry:000044:end -->
<!-- entry:000045:start -->
## [000045] paper — 2026-09-17T08:47:35
arXiv ID: 2005.01864
Title: Streaming Object Detection for 3-D Point Clouds
Authors: Wei Han, Zhengdong Zhang, Benjamin Caine, Brandon Yang, Christoph Sprunk, Ouais Alsharif, Jiquan Ngiam, Vijay Vasudevan, Jonathon Shlens, Zhifeng Chen
Categories: cs.CV
Published: 2020-05-04T21:55:15+00:00
Local file: papers/raw/2005.01864.md (full text retrieved)
Abstract: Autonomous vehicles operate in a dynamic environment, where the speed with which a vehicle can perceive and react impacts the safety and efficacy of the system. LiDAR provides a prominent sensory modality that informs many existing perceptual systems including object detection, segmentation, motion estimation, and action recognition. The latency for perceptual systems based on point cloud data can be dominated by the amount of time for a complete rotational scan (e.g. 100 ms). This built-in data capture latency is artificial, and based on treating the point cloud as a camera image in order to leverage camera-inspired architectures. However, unlike camera sensors, most LiDAR point cloud data is natively a streaming data source in which laser reflections are sequentially recorded based on the precession of the laser beam. In this work, we explore how to build an object detector that removes this artificial latency constraint, and instead operates on native streaming data in order to significantly reduce latency. This approach has the added benefit of reducing the peak computational burden on inference hardware by spreading the computation over the acquisition time for a scan. We demonstrate a family of streaming detection systems based on sequential modeling through a series of modifications to the traditional detection meta-architecture. We highlight how this model may achieve competitive if not superior predictive performance with state-of-the-art, traditional non-streaming detection systems while achieving significant latency gains (e.g. 1/15'th - 1/3'rd of peak latency). Our results show that operating on LiDAR data in its native streaming formulation offers several advantages for self driving object detection -- advantages that we hope will be useful for any LiDAR perception system where minimizing latency is critical for safe and efficient operation.
<!-- entry:000045:end -->
<!-- entry:000046:start -->
## [000046] paper — 2026-09-17T08:47:39
arXiv ID: 2605.31005
Title: Learning Multi-Agent Coordination via Sheaf-ADMM
Authors: Jeffrey Seely, Bartłomiej Cupiał, Llion Jones
Categories: cs.LG
Published: 2026-05-29T08:39:14+00:00
Local file: papers/raw/2605.31005.md (full text retrieved)
Abstract: We present a differentiable optimization framework for multi-agent coordination. An input is decomposed into overlapping local views, each processed by an agent that solves a convex subproblem parameterized by a neural encoder. Agents coordinate through the Alternating Direction Method of Multipliers (ADMM) with inter-agent constraints specified by a cellular sheaf. The sheaf specifies which aspects of neighboring solutions must agree, allowing for heterogeneous notions of global consensus. Backpropagating through the unrolled optimization jointly trains all components of the multi-agent system. We evaluate on maze pathfinding, image classification, and Sudoku, where agents with individually insufficient local views learn to coordinate to produce correct global outputs. On MNIST, the local-view decomposition yields improved robustness to distribution shifts relative to a standard CNN. On Sudoku, the optimization-derived structure yields markedly higher solve rates than parameter-matched MPNN baselines. Finally, the ADMM structure exposes distinct primal, consensus, and dual state variables, opening the coordination dynamics to direct analysis and intervention -- a property unavailable in standard message-passing architectures.
<!-- entry:000046:end -->
<!-- entry:000047:start -->
## [000047] paper — 2026-09-17T08:47:41
arXiv ID: 1905.13678
Title: Learning Sparse Networks Using Targeted Dropout
Authors: Aidan N. Gomez, Ivan Zhang, Siddhartha Rao Kamalakara, Divyam Madaan, Kevin Swersky, Yarin Gal, Geoffrey E. Hinton
Categories: cs.LG, stat.ML
Published: 2019-05-31T15:40:36+00:00
Local file: papers/raw/1905.13678.md (full text retrieved)
Abstract: Neural networks are easier to optimise when they have many more weights than are required for modelling the mapping from inputs to outputs. This suggests a two-stage learning procedure that first learns a large net and then prunes away connections or hidden units. But standard training does not necessarily encourage nets to be amenable to pruning. We introduce targeted dropout, a method for training a neural network so that it is robust to subsequent pruning. Before computing the gradients for each weight update, targeted dropout stochastically selects a set of units or weights to be dropped using a simple self-reinforcing sparsity criterion and then computes the gradients for the remaining weights. The resulting network is robust to post hoc pruning of weights or units that frequently occur in the dropped sets. The method improves upon more complicated sparsifying regularisers while being simple to implement and easy to tune.
<!-- entry:000047:end -->
<!-- entry:000048:start -->
## [000048] paper — 2026-09-17T08:47:45
arXiv ID: 1209.1738
Title: Model Checking the Quantitative mu-Calculus on Linear Hybrid Systems
Authors: Diana Fischer, Lukasz Kaiser
Categories: cs.LO
Published: 2012-09-08T18:22:30+00:00
Local file: papers/raw/1209.1738.md (full text retrieved)
Abstract: We study the model-checking problem for a quantitative extension of the modal mu-calculus on a class of hybrid systems. Qualitative model checking has been proved decidable and implemented for several classes of systems, but this is not the case for quantitative questions that arise naturally in this context. Recently, quantitative formalisms that subsume classical temporal logics and allow the measurement of interesting quantitative phenomena were introduced. We show how a powerful quantitative logic, the quantitative mu-calculus, can be model checked with arbitrary precision on initialised linear hybrid systems. To this end, we develop new techniques for the discretisation of continuous state spaces based on a special class of strategies in model-checking games and present a reduction to a class of counter parity games.
<!-- entry:000048:end -->
<!-- entry:000049:start -->
## [000049] paper — 2026-09-17T08:47:48
arXiv ID: 1702.01806
Title: Beam Search Strategies for Neural Machine Translation
Authors: Markus Freitag, Yaser Al-Onaizan
Categories: cs.CL
Published: 2017-02-06T22:08:46+00:00
Local file: papers/raw/1702.01806.md (full text retrieved)
Abstract: The basic concept in Neural Machine Translation (NMT) is to train a large Neural Network that maximizes the translation performance on a given parallel corpus. NMT is then using a simple left-to-right beam-search decoder to generate new translations that approximately maximize the trained conditional probability. The current beam search strategy generates the target sentence word by word from left-to- right while keeping a fixed amount of active candidates at each time step. First, this simple search is less adaptive as it also expands candidates whose scores are much worse than the current best. Secondly, it does not expand hypotheses if they are not within the best scoring candidates, even if their scores are close to the best one. The latter one can be avoided by increasing the beam size until no performance improvement can be observed. While you can reach better performance, this has the draw- back of a slower decoding speed. In this paper, we concentrate on speeding up the decoder by applying a more flexible beam search strategy whose candidate size may vary at each time step depending on the candidate scores. We speed up the original decoder by up to 43% for the two language pairs German-English and Chinese-English without losing any translation quality.
<!-- entry:000049:end -->
<!-- entry:000050:start -->
## [000050] paper — 2026-09-17T08:47:51
arXiv ID: 2410.03381
Title: Cogs in a Machine, Doing What They're Meant to Do -- The AMI Submission to the WMT24 General Translation Task
Authors: Atli Jasonarson, Hinrik Hafsteinsson, Bjarki Ármannsson, Steinþór Steingrímsson
Categories: cs.CL
Published: 2024-10-04T12:48:32+00:00
Local file: papers/raw/2410.03381.md (full text retrieved)
Abstract: This paper presents the submission of the Árni Magnusson Institute's team to the WMT24 General translation task. We work on the English->Icelandic translation direction. Our system comprises four translation models and a grammar correction model. For training our models we carefully curate our datasets, aggressively filtering out sentence pairs that may detrimentally affect the quality of our system's output. Some of our data are collected from human translations and some are synthetically generated. A part of the synthetic data is generated using an LLM, and we find that it increases the translation capability of our system significantly.
<!-- entry:000050:end -->
<!-- entry:000051:start -->
## [000051] paper — 2026-09-17T08:47:55
arXiv ID: 2508.14472
Title: In2x at WMT25 Translation Task
Authors: Lei Pang, Hanyi Mao, Quanjia Xiao, HaiXiao Liu, Xiangyi Li
Categories: cs.CL, cs.AI
Published: 2025-08-20T06:52:42+00:00
Local file: papers/raw/2508.14472.md (full text retrieved)
Abstract: This paper presents the open-system submission by the In2x research team for the WMT25 General Machine Translation Shared Task. Our submission focuses on Japanese-related translation tasks, aiming to explore a generalizable paradigm for extending large language models (LLMs) to other languages. This paradigm encompasses aspects such as data construction methods and reward model design. The ultimate goal is to enable large language model systems to achieve exceptional performance in low-resource or less commonly spoken languages.
<!-- entry:000051:end -->
<!-- entry:000052:start -->
## [000052] paper — 2026-09-17T08:47:58
arXiv ID: 2407.10855
Title: Weighted Grouped Query Attention in Transformers
Authors: Sai Sena Chinnakonduru, Astarag Mohapatra
Categories: cs.CL, cs.AI
Published: 2024-07-15T16:07:13+00:00
Local file: papers/raw/2407.10855.md (full text retrieved)
Abstract: The attention mechanism forms the foundational blocks for transformer language models. Recent approaches show that scaling the model achieves human-level performance. However, with increasing demands for scaling and constraints on hardware memory, the inference costs of these models remain high. To reduce the inference time, Multi-Query Attention (MQA) and Grouped-Query Attention (GQA) were proposed in (Shazeer, 2019) and (Ainslieet al., 2023) respectively. In this paper, we propose a variation of Grouped-Query Attention, termed Weighted Grouped-Query Attention (WGQA). We introduced new learnable parameters for each key and value head in the T5 decoder attention blocks, enabling the model to take a weighted average during finetuning. Our model achieves an average of 0.53% improvement over GQA, and the performance converges to traditional Multi-head attention (MHA) with no additional overhead during inference. We evaluated the introduction of these parameters and subsequent finetuning informs the model about the grouping mechanism during training, thereby enhancing performance. Additionally, we demonstrate the scaling laws in our analysis by comparing the results between T5-small and T5-base architecture.
<!-- entry:000052:end -->
<!-- entry:000053:start -->
## [000053] paper — 2026-09-17T08:48:02
arXiv ID: 2603.21389
Title: Task-Specific Efficiency Analysis: When Small Language Models Outperform Large Language Models
Authors: Jinghan Cao, Yu Ma, Xinjin Li, Qingyang Ren, Xiangyun Chen
Categories: cs.CL, cs.LG
Published: 2026-03-22T20:19:45+00:00
Local file: papers/raw/2603.21389.md (full text retrieved)
Abstract: Large Language Models achieve remarkable performance but incur substantial computational costs unsuitable for resource-constrained deployments. This paper presents the first comprehensive task-specific efficiency analysis comparing 16 language models across five diverse NLP tasks. We introduce the Performance-Efficiency Ratio (PER), a novel metric integrating accuracy, throughput, memory, and latency through geometric mean normalization. Our systematic evaluation reveals that small models (0.5--3B parameters) achieve superior PER scores across all given tasks. These findings establish quantitative foundations for deploying small models in production environments prioritizing inference efficiency over marginal accuracy gains.
<!-- entry:000053:end -->
<!-- entry:000054:start -->
## [000054] paper — 2026-09-17T08:48:06
arXiv ID: 1705.03122
Title: Convolutional Sequence to Sequence Learning
Authors: Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, Yann N. Dauphin
Categories: cs.CL
Published: 2017-05-08T23:25:30+00:00
Local file: papers/raw/1705.03122.md (full text retrieved)
Abstract: The prevalent approach to sequence to sequence learning maps an input sequence to a variable length output sequence via recurrent neural networks. We introduce an architecture based entirely on convolutional neural networks. Compared to recurrent models, computations over all elements can be fully parallelized during training and optimization is easier since the number of non-linearities is fixed and independent of the input length. Our use of gated linear units eases gradient propagation and we equip each decoder layer with a separate attention module. We outperform the accuracy of the deep LSTM setup of Wu et al. (2016) on both WMT'14 English-German and WMT'14 English-French translation at an order of magnitude faster speed, both on GPU and CPU.
<!-- entry:000054:end -->
<!-- entry:000055:start -->
## [000055] paper — 2026-09-17T08:48:10
arXiv ID: 2402.06894
Title: GenTranslate: Large Language Models are Generative Multilingual Speech and Machine Translators
Authors: Yuchen Hu, Chen Chen, Chao-Han Huck Yang, Ruizhe Li, Dong Zhang, Zhehuai Chen, Eng Siong Chng
Categories: cs.CL, cs.AI, cs.LG, cs.SD, eess.AS
Published: 2024-02-10T07:20:49+00:00
Local file: papers/raw/2402.06894.md (full text retrieved)
Abstract: Recent advances in large language models (LLMs) have stepped forward the development of multilingual speech and machine translation by its reduced representation errors and incorporated external knowledge. However, both translation tasks typically utilize beam search decoding and top-1 hypothesis selection for inference. These techniques struggle to fully exploit the rich information in the diverse N-best hypotheses, making them less optimal for translation tasks that require a single, high-quality output sequence. In this paper, we propose a new generative paradigm for translation tasks, namely "GenTranslate", which builds upon LLMs to generate better results from the diverse translation versions in N-best list. Leveraging the rich linguistic knowledge and strong reasoning abilities of LLMs, our new paradigm can integrate the rich information in N-best candidates to generate a higher-quality translation result. Furthermore, to support LLM finetuning, we build and release a HypoTranslate dataset that contains over 592K hypotheses-translation pairs in 11 languages. Experiments on various speech and machine translation benchmarks (e.g., FLEURS, CoVoST-2, WMT) demonstrate that our GenTranslate significantly outperforms the state-of-the-art model.
<!-- entry:000055:end -->
<!-- entry:000056:start -->
## [000056] paper — 2026-09-17T08:48:15
arXiv ID: 1806.01242
Title: Graph networks as learnable physics engines for inference and control
Authors: Alvaro Sanchez-Gonzalez, Nicolas Heess, Jost Tobias Springenberg, Josh Merel, Martin Riedmiller, Raia Hadsell, Peter Battaglia
Categories: cs.LG, cs.AI, stat.ML
Published: 2018-06-04T17:29:40+00:00
Local file: papers/raw/1806.01242.md (full text retrieved)
Abstract: Understanding and interacting with everyday physical scenes requires rich knowledge about the structure of the world, represented either implicitly in a value or policy function, or explicitly in a transition model. Here we introduce a new class of learnable models--based on graph networks--which implement an inductive bias for object- and relation-centric representations of complex, dynamical systems. Our results show that as a forward model, our approach supports accurate predictions from real and simulated data, and surprisingly strong and efficient generalization, across eight distinct physical systems which we varied parametrically and structurally. We also found that our inference model can perform system identification. Our models are also differentiable, and support online planning via gradient-based trajectory optimization, as well as offline policy optimization. Our framework offers new opportunities for harnessing and exploiting rich knowledge about the world, and takes a key step toward building machines with more human-like representations of the world.
<!-- entry:000056:end -->
<!-- entry:000057:start -->
## [000057] paper — 2026-09-17T08:48:17
arXiv ID: 1710.05941
Title: Searching for Activation Functions
Authors: Prajit Ramachandran, Barret Zoph, Quoc V. Le
Categories: cs.NE, cs.CV, cs.LG
Published: 2017-10-16T18:05:45+00:00
Local file: papers/raw/1710.05941.md (full text retrieved)
Abstract: The choice of activation functions in deep networks has a significant effect on the training dynamics and task performance. Currently, the most successful and widely-used activation function is the Rectified Linear Unit (ReLU). Although various hand-designed alternatives to ReLU have been proposed, none have managed to replace it due to inconsistent gains. In this work, we propose to leverage automatic search techniques to discover new activation functions. Using a combination of exhaustive and reinforcement learning-based search, we discover multiple novel activation functions. We verify the effectiveness of the searches by conducting an empirical evaluation with the best discovered activation function. Our experiments show that the best discovered activation function, $f(x) = x \cdot \text{sigmoid}(βx)$, which we name Swish, tends to work better than ReLU on deeper models across a number of challenging datasets. For example, simply replacing ReLUs with Swish units improves top-1 classification accuracy on ImageNet by 0.9\% for Mobile NASNet-A and 0.6\% for Inception-ResNet-v2. The simplicity of Swish and its similarity to ReLU make it easy for practitioners to replace ReLUs with Swish units in any neural network.
<!-- entry:000057:end -->
<!-- entry:000058:start -->
## [000058] paper — 2026-09-17T08:48:20
arXiv ID: 1903.00925
Title: Accelerating Training of Deep Neural Networks with a Standardization Loss
Authors: Jasmine Collins, Johannes Balle, Jonathon Shlens
Categories: cs.LG, cs.AI, cs.CV, stat.ML
Published: 2019-03-03T15:17:06+00:00
Local file: papers/raw/1903.00925.md (full text retrieved)
Abstract: A significant advance in accelerating neural network training has been the development of normalization methods, permitting the training of deep models both faster and with better accuracy. These advances come with practical challenges: for instance, batch normalization ties the prediction of individual examples with other examples within a batch, resulting in a network that is heavily dependent on batch size. Layer normalization and group normalization are data-dependent and thus must be continually used, even at test-time. To address the issues that arise from using explicit normalization techniques, we propose to replace existing normalization methods with a simple, secondary objective loss that we term a standardization loss. This formulation is flexible and robust across different batch sizes and surprisingly, this secondary objective accelerates learning on the primary training objective. Because it is a training loss, it is simply removed at test-time, and no further effort is needed to maintain normalized activations. We find that a standardization loss accelerates training on both small- and large-scale image classification experiments, works with a variety of architectures, and is largely robust to training across different batch sizes.
<!-- entry:000058:end -->
<!-- entry:000059:start -->
## [000059] paper — 2026-09-17T08:48:25
arXiv ID: 2408.04242
Title: The Ungrounded Alignment Problem
Authors: Marc Pickett, Aakash Kumar Nain, Joseph Modayil, Llion Jones
Categories: cs.LG, cs.AI, cs.NE
Published: 2024-08-08T06:08:04+00:00
Local file: papers/raw/2408.04242.md (full text retrieved)
Abstract: Modern machine learning systems have demonstrated substantial abilities with methods that either embrace or ignore human-provided knowledge, but combining benefits of both styles remains a challenge. One particular challenge involves designing learning systems that exhibit built-in responses to specific abstract stimulus patterns, yet are still plastic enough to be agnostic about the modality and exact form of their inputs. In this paper, we investigate what we call The Ungrounded Alignment Problem, which asks How can we build in predefined knowledge in a system where we don't know how a given stimulus will be grounded? This paper examines a simplified version of the general problem, where an unsupervised learner is presented with a sequence of images for the characters in a text corpus, and this learner is later evaluated on its ability to recognize specific (possibly rare) sequential patterns. Importantly, the learner is given no labels during learning or evaluation, but must map images from an unknown font or permutation to its correct class label. That is, at no point is our learner given labeled images, where an image vector is explicitly associated with a class label. Despite ample work in unsupervised and self-supervised loss functions, all current methods require a labeled fine-tuning phase to map the learned representations to correct classes. Finding this mapping in the absence of labels may seem a fool's errand, but our main result resolves this seeming paradox. We show that leveraging only letter bigram frequencies is sufficient for an unsupervised learner both to reliably associate images to class labels and to reliably identify trigger words in the sequence of inputs. More generally, this method suggests an approach for encoding specific desired innate behaviour in modality-agnostic models.
<!-- entry:000059:end -->
<!-- entry:000060:start -->
## [000060] paper — 2026-09-17T08:48:42
arXiv ID: 1706.03059
Title: Depthwise Separable Convolutions for Neural Machine Translation
Authors: Lukasz Kaiser, Aidan N. Gomez, Francois Chollet
Categories: cs.CL, cs.LG
Published: 2017-06-09T17:59:16+00:00
Local file: papers/raw/1706.03059.md (full text retrieved)
Abstract: Depthwise separable convolutions reduce the number of parameters and computation used in convolutional operations while increasing representational efficiency. They have been shown to be successful in image classification models, both in obtaining better models than previously possible for a given parameter count (the Xception architecture) and considerably reducing the number of parameters required to perform at a given level (the MobileNets family of architectures). Recently, convolutional sequence-to-sequence networks have been applied to machine translation tasks with good results. In this work, we study how depthwise separable convolutions can be applied to neural machine translation. We introduce a new architecture inspired by Xception and ByteNet, called SliceNet, which enables a significant reduction of the parameter count and amount of computation needed to obtain results like ByteNet, and, with a similar parameter count, achieves new state-of-the-art results. In addition to showing that depthwise separable convolutions perform well for machine translation, we investigate the architectural changes that they enable: we observe that thanks to depthwise separability, we can increase the length of convolution windows, removing the need for filter dilation. We also introduce a new "super-separable" convolution operation that further reduces the number of parameters and computational cost for obtaining state-of-the-art results.
<!-- entry:000060:end -->
<!-- entry:000061:start -->
## [000061] paper — 2026-09-17T08:49:01
arXiv ID: 1511.08228
Title: Neural GPUs Learn Algorithms
Authors: Łukasz Kaiser, Ilya Sutskever
Categories: cs.LG, cs.NE
Published: 2015-11-25T21:17:43+00:00
Local file: papers/raw/1511.08228.md (full text retrieved)
Abstract: Learning an algorithm from examples is a fundamental problem that has been widely studied. Recently it has been addressed using neural networks, in particular by Neural Turing Machines (NTMs). These are fully differentiable computers that use backpropagation to learn their own programming. Despite their appeal NTMs have a weakness that is caused by their sequential nature: they are not parallel and are are hard to train due to their large depth when unfolded.   We present a neural network architecture to address this problem: the Neural GPU. It is based on a type of convolutional gated recurrent unit and, like the NTM, is computationally universal. Unlike the NTM, the Neural GPU is highly parallel which makes it easier to train and efficient to run.   An essential property of algorithms is their ability to handle inputs of arbitrary size. We show that the Neural GPU can be trained on short instances of an algorithmic task and successfully generalize to long instances. We verified it on a number of tasks including long addition and long multiplication of numbers represented in binary. We train the Neural GPU on numbers with upto 20 bits and observe no errors whatsoever while testing it, even on much longer numbers.   To achieve these results we introduce a technique for training deep recurrent networks: parameter sharing relaxation. We also found a small amount of dropout and gradient noise to have a large positive effect on learning and generalization.
<!-- entry:000061:end -->
<!-- entry:000062:start -->
## [000062] paper — 2026-09-17T08:49:04
arXiv ID: 1809.00357
Title: Trivial Transfer Learning for Low-Resource Neural Machine Translation
Authors: Tom Kocmi, Ondřej Bojar
Categories: cs.CL
Published: 2018-09-02T15:24:15+00:00
Local file: papers/raw/1809.00357.md (full text retrieved)
Abstract: Transfer learning has been proven as an effective technique for neural machine translation under low-resource conditions. Existing methods require a common target language, language relatedness, or specific training tricks and regimes. We present a simple transfer learning method, where we first train a "parent" model for a high-resource language pair and then continue the training on a lowresource pair only by replacing the training corpus. This "child" model performs significantly better than the baseline trained for lowresource pair only. We are the first to show this for targeting different languages, and we observe the improvements even for unrelated languages with different alphabets.
<!-- entry:000062:end -->
<!-- entry:000063:start -->
## [000063] paper — 2026-09-17T10:17:18
arXiv ID: 2103.05103
Title: Image Captioning using Multiple Transformers for Self-Attention Mechanism
Authors: Farrukh Olimov, Shikha Dubey, Labina Shrestha, Tran Trung Tin, Moongu Jeon
Categories: cs.CV, cs.AI, cs.CL
Published: 2021-02-14T05:35:54+00:00
Local file: papers/raw/2103.05103.md (full text retrieved)
Abstract: Real-time image captioning, along with adequate precision, is the main challenge of this research field. The present work, Multiple Transformers for Self-Attention Mechanism (MTSM), utilizes multiple transformers to address these problems. The proposed algorithm, MTSM, acquires region proposals using a transformer detector (DETR). Consequently, MTSM achieves the self-attention mechanism by transferring these region proposals and their visual and geometrical features through another transformer and learns the objects' local and global interconnections. The qualitative and quantitative results of the proposed algorithm, MTSM, are shown on the MSCOCO dataset.
<!-- entry:000063:end -->
<!-- entry:000064:start -->
## [000064] paper — 2026-09-17T10:17:20
arXiv ID: 2007.13199
Title: Double Multi-Head Attention for Speaker Verification
Authors: Miquel India, Pooyan Safari, Javier Hernando
Categories: eess.AS, cs.SD
Published: 2020-07-26T19:18:53+00:00
Local file: papers/raw/2007.13199.md (full text retrieved)
Abstract: Most state-of-the-art Deep Learning systems for speaker verification are based on speaker embedding extractors. These architectures are commonly composed of a feature extractor front-end together with a pooling layer to encode variable-length utterances into fixed-length speaker vectors. In this paper we present Double Multi-Head Attention pooling, which extends our previous approach based on Self Multi-Head Attention. An additional self attention layer is added to the pooling layer that summarizes the context vectors produced by Multi-Head Attention into a unique speaker representation. This method enhances the pooling mechanism by giving weights to the information captured for each head and it results in creating more discriminative speaker embeddings. We have evaluated our approach with the VoxCeleb2 dataset. Our results show 6.09% and 5.23% relative improvement in terms of EER compared to Self Attention pooling and Self Multi-Head Attention, respectively. According to the obtained results, Double Multi-Head Attention has shown to be an excellent approach to efficiently select the most relevant features captured by the CNN-based front-ends from the speech signal.
<!-- entry:000064:end -->
<!-- entry:000065:start -->
## [000065] paper — 2026-09-17T10:17:24
arXiv ID: 2506.04956
Title: FEAT: Full-Dimensional Efficient Attention Transformer for Medical Video Generation
Authors: Huihan Wang, Zhiwen Yang, Hui Zhang, Dan Zhao, Bingzheng Wei, Yan Xu
Categories: cs.CV
Published: 2025-06-05T12:31:02+00:00
Local file: papers/raw/2506.04956.md (full text retrieved)
Abstract: Synthesizing high-quality dynamic medical videos remains a significant challenge due to the need for modeling both spatial consistency and temporal dynamics. Existing Transformer-based approaches face critical limitations, including insufficient channel interactions, high computational complexity from self-attention, and coarse denoising guidance from timestep embeddings when handling varying noise levels. In this work, we propose FEAT, a full-dimensional efficient attention Transformer, which addresses these issues through three key innovations: (1) a unified paradigm with sequential spatial-temporal-channel attention mechanisms to capture global dependencies across all dimensions, (2) a linear-complexity design for attention mechanisms in each dimension, utilizing weighted key-value attention and global channel attention, and (3) a residual value guidance module that provides fine-grained pixel-level guidance to adapt to different noise levels. We evaluate FEAT on standard benchmarks and downstream tasks, demonstrating that FEAT-S, with only 23\% of the parameters of the state-of-the-art model Endora, achieves comparable or even superior performance. Furthermore, FEAT-L surpasses all comparison methods across multiple datasets, showcasing both superior effectiveness and scalability. Code is available at https://github.com/Yaziwel/FEAT.
<!-- entry:000065:end -->
<!-- entry:000066:start -->
## [000066] paper — 2026-09-17T10:17:28
arXiv ID: 2607.07953
Title: Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing
Authors: Tommaso Cerruti, Tim Rieder, George Rowlands, Lingfeng Jin, Imanol Schlag
Categories: cs.LG, cs.AI
Published: 2026-07-08T22:14:14+00:00
Local file: papers/raw/2607.07953.md (full text retrieved)
Abstract: Self-attention lets each token retrieve information from the full context, but its quadratic cost in sequence length limits training and inference at long context. This paper presents a comparative study of softmax attention and four recent recurrent linear-attention architectures: DeltaNet, Gated DeltaNet, Kimi Delta Attention, and Gated DeltaNet-2. We express these mechanisms in a common recurrent-memory notation, making explicit how they differ in expressivity, memory decay, erase and write control, training throughput, and implementation complexity. Our experiments center on 350M-parameter models trained for 15B tokens, and include optimizer and learning-rate comparisons, hybrid-versus-pure stack comparisons, sequence-length runtime measurements, larger DeltaNet runs at 1.3B and 3B parameters, and a small set of downstream evaluations. The reported speed results measure training throughput and iteration time; we do not provide an empirical inference-speed benchmark. Within the reported 350M-parameter, 15B-token sweep, Kimi Delta Attention with Muon reaches the lowest final validation loss, a pure Gated DeltaNet stack trained with AdamW has the highest normalized training throughput, hybrid stacks generally improve loss at a throughput cost, and Muon consistently lowers final validation loss relative to AdamW in the matched architecture settings we evaluate. We introduce and evaluate lightweight cross-layer routing mechanisms for DeltaNet-style memories. The most natural DeltaNet-inspired formulation, forwarding a lower layer's delta-rule write error into the next layer's value target, does not improve over matched baselines. Routing into the aligned hidden stream and forwarding the write value instead yields a modest improvement in the matched runs we report: Cross-Layer Value Routing (CLVR) lowers final validation loss for both DeltaNet and Gated DeltaNet.
<!-- entry:000066:end -->
<!-- entry:000067:start -->
## [000067] paper — 2026-09-17T10:17:30
arXiv ID: 2601.15305
Title: Gated Sparse Attention: Combining Computational Efficiency with Training Stability for Long-Context Language Models
Authors: Alfred Shen, Aaron Shen
Categories: cs.AI
Published: 2026-01-12T20:33:39+00:00
Local file: papers/raw/2601.15305.md (full text retrieved)
Abstract: The computational burden of attention in long-context language models has motivated two largely independent lines of work: sparse attention mechanisms that reduce complexity by attending to selected tokens, and gated attention variants that improve training sta-bility while mitigating the attention sink phenomenon. We observe that these approaches address complementary weaknesses and propose Gated Sparse Attention (GSA), an architecture that realizes the benefits of both. GSA incorporates a gated lightning indexer with sigmoid activations that produce bounded, interpretable selection scores, an adaptive sparsity controller that modulates the number of attended tokens based on local uncertainty, and dual gating at the value and output stages. We establish theoretical foundations for the approach, including complexity analysis, expressiveness results, and convergence guarantees. In experiments with 1.7B parameter models trained on 400B tokens, GSA matches the efficiency of sparse-only baselines (12-16x speedup at 128K context) while achieving the quality gains associated with gated attention: perplexity improves from 6.03 to 5.70, RULER scores at 128K context nearly double, and attention to the first token, a proxy for attention sinks, drops from 47% to under 4%. Training stability improves markedly, with loss spikes reduced by 98%.
<!-- entry:000067:end -->
<!-- entry:000068:start -->
## [000068] paper — 2026-09-17T10:17:35
arXiv ID: 2303.17696
Title: Dual Cross-Attention for Medical Image Segmentation
Authors: Gorkem Can Ates, Prasoon Mohan, Emrah Celik
Categories: cs.CV, cs.LG, eess.IV
Published: 2023-03-30T20:24:57+00:00
Local file: papers/raw/2303.17696.md (full text retrieved)
Abstract: We propose Dual Cross-Attention (DCA), a simple yet effective attention module that is able to enhance skip-connections in U-Net-based architectures for medical image segmentation. DCA addresses the semantic gap between encoder and decoder features by sequentially capturing channel and spatial dependencies across multi-scale encoder features. First, the Channel Cross-Attention (CCA) extracts global channel-wise dependencies by utilizing cross-attention across channel tokens of multi-scale encoder features. Then, the Spatial Cross-Attention (SCA) module performs cross-attention to capture spatial dependencies across spatial tokens. Finally, these fine-grained encoder features are up-sampled and connected to their corresponding decoder parts to form the skip-connection scheme. Our proposed DCA module can be integrated into any encoder-decoder architecture with skip-connections such as U-Net and its variants. We test our DCA module by integrating it into six U-Net-based architectures such as U-Net, V-Net, R2Unet, ResUnet++, DoubleUnet and MultiResUnet. Our DCA module shows Dice Score improvements up to 2.05% on GlaS, 2.74% on MoNuSeg, 1.37% on CVC-ClinicDB, 1.12% on Kvasir-Seg and 1.44% on Synapse datasets. Our codes are available at: https://github.com/gorkemcanates/Dual-Cross-Attention
<!-- entry:000068:end -->
<!-- entry:000069:start -->
## [000069] paper — 2026-09-17T10:17:38
arXiv ID: 2512.07011
Title: Block Sparse Flash Attention
Authors: Daniel Ohayon, Itay Lamprecht, Itay Hubara, Israel Cohen, Daniel Soudry, Noam Elata
Categories: cs.LG, cs.CL, cs.PF
Published: 2025-12-07T21:20:12+00:00
Local file: papers/raw/2512.07011.md (full text retrieved)
Abstract: Modern large language models increasingly require long contexts for reasoning and multi-document tasks, but attention's quadratic complexity creates a severe computational bottleneck. We present Block-Sparse FlashAttention (BSFA), a drop-in replacement that accelerates long-context inference while preserving model quality. Unlike methods that predict importance before computing scores, BSFA computes exact query-key similarities to select the top-k most important value blocks for each query. By comparing per-block maximum scores against calibrated thresholds, we skip approximately 50% of the computation and memory transfers for pruned blocks. Our training-free approach requires only a one-time threshold calibration on a small dataset to learn the per-layer and per-head attention score distributions. We provide a CUDA kernel implementation that can be used as a drop-in replacement for FlashAttention. On Llama-3.1-8B, BSFA achieves up to 1.10x speedup on real-world reasoning benchmarks and up to 1.24x for needle-in-a-haystack retrieval tasks while maintaining above 99% baseline accuracy, with certain configurations even improving accuracy by focusing on the most relevant content, substantially outperforming existing sparse attention methods. The implementation is available at https://github.com/Danielohayon/Block-Sparse-Flash-Attention
<!-- entry:000069:end -->
<!-- entry:000070:start -->
## [000070] paper — 2026-09-17T10:17:41
arXiv ID: 2604.21816
Title: Tool Attention Is All You Need: Dynamic Tool Gating and Lazy Schema Loading for Eliminating the MCP/Tools Tax in Scalable Agentic Workflows
Authors: Anuj Sadani, Deepak Kumar
Categories: cs.AI
Published: 2026-04-23T16:10:00+00:00
Local file: papers/raw/2604.21816.md (full text retrieved)
Abstract: The Model Context Protocol (MCP) has become a common interface for connecting large language model (LLM) agents to external tools, but its reliance on stateless, eager schema injection imposes a hidden per-turn overhead the MCP Tax or Tools Tax that practitioner reports place between roughly 10k and 60k tokens in typical multi-server deployments. This payload inflates the key-value cache, is associated with reasoning degradation as context utilization approaches published fracture points around 70%, and turns token budgets into a recurring operational cost. We introduce Tool Attention, a middleware-layer mechanism that generalizes the "Attention Is All You Need" paradigm from self-attention over tokens to gated attention over tools. Tool Attention combines (i) an Intent Schema Overlap (ISO) score from sentence embeddings, (ii) a state-aware gating function enforcing preconditions and access scopes, and (iii) a two-phase lazy schema loader that keeps a compact summary pool in context and promotes full JSON schemas only for top-k gated tools. We evaluate on a simulated 120-tool, six-server benchmark whose per-server token counts are calibrated to public audits of real MCP deployments. In this simulation, Tool Attention directly reduces measured per-turn tool tokens by 95.0% (47.3k -> 2.4k) and raises effective context utilization (a token-ratio quantity) from 24% to 91%. End-to-end figures for task success, latency, cost, and reasoning quality are reported as projections derived from the measured token counts combined with published deployment telemetry; they are not measured on live LLM agents, and we mark projected values explicitly throughout. Taken together, the results support a simple thesis: protocol-level efficiency, not raw context length, is a binding constraint on scalable gentic systems. The code for this work is accessible at https://github.com/asadani/tool-attention
<!-- entry:000070:end -->
<!-- entry:000071:start -->
## [000071] paper — 2026-09-17T10:17:45
arXiv ID: 1808.02822
Title: Backprop Evolution
Authors: Maximilian Alber, Irwan Bello, Barret Zoph, Pieter-Jan Kindermans, Prajit Ramachandran, Quoc Le
Categories: cs.NE, cs.LG, stat.ML
Published: 2018-08-08T15:23:14+00:00
Local file: papers/raw/1808.02822.md (full text retrieved)
Abstract: The back-propagation algorithm is the cornerstone of deep learning. Despite its importance, few variations of the algorithm have been attempted. This work presents an approach to discover new variations of the back-propagation equation. We use a domain specific lan- guage to describe update equations as a list of primitive functions. An evolution-based method is used to discover new propagation rules that maximize the generalization per- formance after a few epochs of training. We find several update equations that can train faster with short training times than standard back-propagation, and perform similar as standard back-propagation at convergence.
<!-- entry:000071:end -->
<!-- entry:000072:start -->
## [000072] paper — 2026-09-17T10:17:48
arXiv ID: 1908.11069
Title: StarNet: Targeted Computation for Object Detection in Point Clouds
Authors: Jiquan Ngiam, Benjamin Caine, Wei Han, Brandon Yang, Yuning Chai, Pei Sun, Yin Zhou, Xi Yi, Ouais Alsharif, Patrick Nguyen, Zhifeng Chen, Jonathon Shlens, Vijay Vasudevan
Categories: cs.CV
Published: 2019-08-29T06:54:46+00:00
Local file: papers/raw/1908.11069.md (full text retrieved)
Abstract: Detecting objects from LiDAR point clouds is an important component of self-driving car technology as LiDAR provides high resolution spatial information. Previous work on point-cloud 3D object detection has re-purposed convolutional approaches from traditional camera imagery. In this work, we present an object detection system called StarNet designed specifically to take advantage of the sparse and 3D nature of point cloud data. StarNet is entirely point-based, uses no global information, has data dependent anchors, and uses sampling instead of learned region proposals. We demonstrate how this design leads to competitive or superior performance on the large Waymo Open Dataset and the KITTI detection dataset, as compared to convolutional baselines. In particular, we show how our detector can outperform a competitive baseline on Pedestrian detection on the Waymo Open Dataset by more than 7 absolute mAP while being more computationally efficient. We show how our redesign---namely using only local information and using sampling instead of learned proposals---leads to a significantly more flexible and adaptable system: we demonstrate how we can vary the computational cost of a single trained StarNet without retraining, and how we can target proposals towards areas of interest with priors and heuristics. Finally, we show how our design allows for incorporating temporal context by using detections from previous frames to target computation of the detector, which leads to further improvements in performance without additional computational cost.
<!-- entry:000072:end -->
<!-- entry:000073:start -->
## [000073] paper — 2026-09-17T10:17:54
arXiv ID: 2311.16738
Title: Riemannian Self-Attention Mechanism for SPD Networks
Authors: Rui Wang, Xiao-Jun Wu, Hui Li, Josef Kittler
Categories: cs.CV
Published: 2023-11-28T12:34:46+00:00
Local file: papers/raw/2311.16738.md (full text retrieved)
Abstract: Symmetric positive definite (SPD) matrix has been demonstrated to be an effective feature descriptor in many scientific areas, as it can encode spatiotemporal statistics of the data adequately on a curved Riemannian manifold, i.e., SPD manifold. Although there are many different ways to design network architectures for SPD matrix nonlinear learning, very few solutions explicitly mine the geometrical dependencies of features at different layers. Motivated by the great success of self-attention mechanism in capturing long-range relationships, an SPD manifold self-attention mechanism (SMSA) is proposed in this paper using some manifold-valued geometric operations, mainly the Riemannian metric, Riemannian mean, and Riemannian optimization. Then, an SMSA-based geometric learning module (SMSA-GLM) is designed for the sake of improving the discrimination of the generated deep structured representations. Extensive experimental results achieved on three benchmarking datasets show that our modification against the baseline network further alleviates the information degradation problem and leads to improved accuracy.
<!-- entry:000073:end -->
<!-- entry:000074:start -->
## [000074] paper — 2026-09-17T10:18:00
arXiv ID: 2401.17426
Title: Superiority of Multi-Head Attention in In-Context Linear Regression
Authors: Yingqian Cui, Jie Ren, Pengfei He, Jiliang Tang, Yue Xing
Categories: cs.LG, cs.AI, stat.ML
Published: 2024-01-30T20:29:06+00:00
Local file: papers/raw/2401.17426.md (full text retrieved)
Abstract: We present a theoretical analysis of the performance of transformer with softmax attention in in-context learning with linear regression tasks. While the existing literature predominantly focuses on the convergence of transformers with single-/multi-head attention, our research centers on comparing their performance. We conduct an exact theoretical analysis to demonstrate that multi-head attention with a substantial embedding dimension performs better than single-head attention. When the number of in-context examples D increases, the prediction loss using single-/multi-head attention is in O(1/D), and the one for multi-head attention has a smaller multiplicative constant. In addition to the simplest data distribution setting, we consider more scenarios, e.g., noisy labels, local examples, correlated features, and prior knowledge. We observe that, in general, multi-head attention is preferred over single-head attention. Our results verify the effectiveness of the design of multi-head attention in the transformer architecture.
<!-- entry:000074:end -->
<!-- entry:000075:start -->
## [000075] paper — 2026-09-17T10:18:02
arXiv ID: 2311.13657
Title: Efficient Transformer Knowledge Distillation: A Performance Review
Authors: Nathan Brown, Ashton Williamson, Tahj Anderson, Logan Lawrence
Categories: cs.CL, cs.LG
Published: 2023-11-22T19:19:37+00:00
Local file: papers/raw/2311.13657.md (full text retrieved)
Abstract: As pretrained transformer language models continue to achieve state-of-the-art performance, the Natural Language Processing community has pushed for advances in model compression and efficient attention mechanisms to address high computational requirements and limited input sequence length. Despite these separate efforts, no investigation has been done into the intersection of these two fields. In this work, we provide an evaluation of model compression via knowledge distillation on efficient attention transformers. We provide cost-performance trade-offs for the compression of state-of-the-art efficient attention architectures and the gains made in performance in comparison to their full attention counterparts. Furthermore, we introduce a new long-context Named Entity Recognition dataset, GONERD, to train and test the performance of NER models on long sequences. We find that distilled efficient attention transformers can preserve a significant amount of original model performance, preserving up to 98.6% across short-context tasks (GLUE, SQUAD, CoNLL-2003), up to 94.6% across long-context Question-and-Answering tasks (HotpotQA, TriviaQA), and up to 98.8% on long-context Named Entity Recognition (GONERD), while decreasing inference times by up to 57.8%. We find that, for most models on most tasks, performing knowledge distillation is an effective method to yield high-performing efficient attention models with low costs.
<!-- entry:000075:end -->
<!-- entry:000076:start -->
## [000076] paper — 2026-09-17T10:18:05
arXiv ID: 2606.10650
Title: Dynamic Linear Attention
Authors: Xin Wang, Hui Shen, Boyuan Zheng, Xueshen Liu, Minkyoung Cho, Zhongwei Wan, Zesen Zhao, Zhuoqing Mao, Shen Yan, Mi Zhang
Categories: cs.CL, cs.AI
Published: 2026-06-09T09:57:48+00:00
Local file: papers/raw/2606.10650.md (full text retrieved)
Abstract: The scalability of Large Language Models (LLMs) to long contexts is fundamentally constrained by the quadratic complexity of standard attention, motivating the adoption of linear attention mechanisms with sub-quadratic cost. To improve representation capacity under long contexts, recent approaches organize memory in a multi-state manner. However, existing multi-state linear attention methods rely on fixed state merging policies that cannot adapt to dynamically varying token importance, irreversibly obscuring critical tokens and causing severe error accumulation over long sequences. To address this limitation, we propose DLA, a dynamic memory modeling framework for multi-state linear attention. DLA introduces (i) Information-Aware Dynamic State Merging, which adaptively determines state boundaries based on token-level information variation, preserving high-resolution representations around semantic transitions while aggressively summarizing stable regions, and (ii) Capacity-Bounded Memory Modeling, which maintains a fixed-size, chronologically ordered state cache by selectively merging adjacent low-information states to control memory growth with minimal information loss. We pre-train DLA on two different linear attention models and evaluate on 16 datasets across three categories. Experimental results demonstrate the superiority of DLA over state-of-the-art.
<!-- entry:000076:end -->
<!-- entry:000077:start -->
## [000077] paper — 2026-09-17T10:18:20
arXiv ID: 2502.18137
Title: SpargeAttention: Accurate and Training-free Sparse Attention Accelerating Any Model Inference
Authors: Jintao Zhang, Chendong Xiang, Haofeng Huang, Jia Wei, Haocheng Xi, Jun Zhu, Jianfei Chen
Categories: cs.LG, cs.AI, cs.CV, cs.PF
Published: 2025-02-25T12:02:17+00:00
Local file: papers/raw/2502.18137.md (full text retrieved)
Abstract: An efficient attention implementation is essential for large models due to its quadratic time complexity. Fortunately, attention commonly exhibits sparsity, i.e., many values in the attention map are near zero, allowing for the omission of corresponding computations. Many studies have utilized the sparse pattern to accelerate attention. However, most existing works focus on optimizing attention within specific models by exploiting certain sparse patterns of the attention map. A universal sparse attention that guarantees both the speedup and end-to-end performance of diverse models remains elusive. In this paper, we propose SpargeAttn, a universal sparse and quantized attention for any model. Our method uses a two-stage online filter: in the first stage, we rapidly and accurately predict the attention map, enabling the skip of some matrix multiplications in attention. In the second stage, we design an online softmax-aware filter that incurs no extra overhead and further skips some matrix multiplications. Experiments show that our method significantly accelerates diverse models, including language, image, and video generation, without sacrificing end-to-end metrics. The code is available at https://github.com/thu-ml/SpargeAttn.
<!-- entry:000077:end -->
<!-- entry:000078:start -->
## [000078] paper — 2026-09-17T10:18:27
arXiv ID: 2505.08426
Title: DHECA-SuperGaze: Dual Head-Eye Cross-Attention and Super-Resolution for Unconstrained Gaze Estimation
Authors: Franko Šikić, Donik Vršnak, Sven Lončarić
Categories: cs.CV
Published: 2025-05-13T10:45:08+00:00
Local file: papers/raw/2505.08426.md (full text retrieved)
Abstract: Unconstrained gaze estimation is the process of determining where a subject is directing their visual attention in uncontrolled environments. Gaze estimation systems are important for a myriad of tasks such as driver distraction monitoring, exam proctoring, accessibility features in modern software, etc. However, these systems face challenges in real-world scenarios, partially due to the low resolution of in-the-wild images and partially due to insufficient modeling of head-eye interactions in current state-of-the-art (SOTA) methods. This paper introduces DHECA-SuperGaze, a deep learning-based method that advances gaze prediction through super-resolution (SR) and a dual head-eye cross-attention (DHECA) module. Our dual-branch convolutional backbone processes eye and multiscale SR head images, while the proposed DHECA module enables bidirectional feature refinement between the extracted visual features through cross-attention mechanisms. Furthermore, we identified critical annotation errors in one of the most diverse and widely used gaze estimation datasets, Gaze360, and rectified the mislabeled data. Performance evaluation on Gaze360 and GFIE datasets demonstrates superior within-dataset performance of the proposed method, reducing angular error (AE) by 0.48° (Gaze360) and 2.95° (GFIE) in static configurations, and 0.59° (Gaze360) and 3.00° (GFIE) in temporal settings compared to prior SOTA methods. Cross-dataset testing shows improvements in AE of more than 1.53° (Gaze360) and 3.99° (GFIE) in both static and temporal settings, validating the robust generalization properties of our approach.
<!-- entry:000078:end -->
<!-- entry:000079:start -->
## [000079] paper — 2026-09-17T10:18:45
arXiv ID: 2405.02803
Title: Is Flash Attention Stable?
Authors: Alicia Golden, Samuel Hsia, Fei Sun, Bilge Acun, Basil Hosmer, Yejin Lee, Zachary DeVito, Jeff Johnson, Gu-Yeon Wei, David Brooks, Carole-Jean Wu
Categories: cs.LG, cs.DC
Published: 2024-05-05T03:25:25+00:00
Local file: papers/raw/2405.02803.md (full text retrieved)
Abstract: Training large-scale machine learning models poses distinct system challenges, given both the size and complexity of today's workloads. Recently, many organizations training state-of-the-art Generative AI models have reported cases of instability during training, often taking the form of loss spikes. Numeric deviation has emerged as a potential cause of this training instability, although quantifying this is especially challenging given the costly nature of training runs. In this work, we develop a principled approach to understanding the effects of numeric deviation, and construct proxies to put observations into context when downstream effects are difficult to quantify. As a case study, we apply this framework to analyze the widely-adopted Flash Attention optimization. We find that Flash Attention sees roughly an order of magnitude more numeric deviation as compared to Baseline Attention at BF16 when measured during an isolated forward pass. We then use a data-driven analysis based on the Wasserstein Distance to provide upper bounds on how this numeric deviation impacts model weights during training, finding that the numerical deviation present in Flash Attention is 2-5 times less significant than low-precision training.
<!-- entry:000079:end -->
<!-- entry:000080:start -->
## [000080] paper — 2026-09-17T10:18:49
arXiv ID: 2104.04692
Title: Not All Attention Is All You Need
Authors: Hongqiu Wu, Hai Zhao, Min Zhang
Categories: cs.CL
Published: 2021-04-10T06:24:52+00:00
Local file: papers/raw/2104.04692.md (full text retrieved)
Abstract: Beyond the success story of pre-trained language models (PrLMs) in recent natural language processing, they are susceptible to over-fitting due to unusual large model size. To this end, dropout serves as a therapy. However, existing methods like random-based, knowledge-based and search-based dropout are more general but less effective onto self-attention based models, which are broadly chosen as the fundamental architecture of PrLMs. In this paper, we propose a novel dropout method named AttendOut to let self-attention empowered PrLMs capable of more robust task-specific tuning. We demonstrate that state-of-the-art models with elaborate training design may achieve much stronger results. We verify the universality of our approach on extensive natural language processing tasks.
<!-- entry:000080:end -->
<!-- entry:000081:start -->
## [000081] paper — 2026-09-17T10:18:53
arXiv ID: 1810.02019
Title: Seq2Slate: Re-ranking and Slate Optimization with RNNs
Authors: Irwan Bello, Sayali Kulkarni, Sagar Jain, Craig Boutilier, Ed Chi, Elad Eban, Xiyang Luo, Alan Mackey, Ofer Meshi
Categories: cs.IR, cs.LG, stat.ML
Published: 2018-10-04T01:35:14+00:00
Local file: papers/raw/1810.02019.md (full text retrieved)
Abstract: Ranking is a central task in machine learning and information retrieval. In this task, it is especially important to present the user with a slate of items that is appealing as a whole. This in turn requires taking into account interactions between items, since intuitively, placing an item on the slate affects the decision of which other items should be placed alongside it. In this work, we propose a sequence-to-sequence model for ranking called seq2slate. At each step, the model predicts the next `best' item to place on the slate given the items already selected. The sequential nature of the model allows complex dependencies between the items to be captured directly in a flexible and scalable way. We show how to learn the model end-to-end from weak supervision in the form of easily obtained click-through data. We further demonstrate the usefulness of our approach in experiments on standard ranking benchmarks as well as in a real-world recommendation system.
<!-- entry:000081:end -->
<!-- entry:000082:start -->
## [000082] paper — 2026-09-17T10:18:56
arXiv ID: 2310.11398
Title: Neural Attention: Enhancing QKV Calculation in Self-Attention Mechanism with Neural Networks
Authors: Muhan Zhang
Categories: cs.CL, cs.AI
Published: 2023-10-17T17:06:26+00:00
Local file: papers/raw/2310.11398.md (full text retrieved)
Abstract: In the realm of deep learning, the self-attention mechanism has substantiated its pivotal role across a myriad of tasks, encompassing natural language processing and computer vision. Despite achieving success across diverse applications, the traditional self-attention mechanism primarily leverages linear transformations for the computation of query, key, and value (QKV), which may not invariably be the optimal choice under specific circumstances. This paper probes into a novel methodology for QKV computation-implementing a specially-designed neural network structure for the calculation. Utilizing a modified Marian model, we conducted experiments on the IWSLT 2017 German-English translation task dataset and juxtaposed our method with the conventional approach. The experimental results unveil a significant enhancement in BLEU scores with our method. Furthermore, our approach also manifested superiority when training the Roberta model with the Wikitext-103 dataset, reflecting a notable reduction in model perplexity compared to its original counterpart. These experimental outcomes not only validate the efficacy of our method but also reveal the immense potential in optimizing the self-attention mechanism through neural network-based QKV computation, paving the way for future research and practical applications. The source code and implementation details for our proposed method can be accessed at https://github.com/ocislyjrti/NeuralAttention.
<!-- entry:000082:end -->
<!-- entry:000083:start -->
## [000083] paper — 2026-09-17T10:19:00
arXiv ID: 2410.11842
Title: MoH: Multi-Head Attention as Mixture-of-Head Attention
Authors: Peng Jin, Bo Zhu, Li Yuan, Shuicheng Yan
Categories: cs.CV, cs.AI, cs.LG
Published: 2024-10-15T17:59:44+00:00
Local file: papers/raw/2410.11842.md (full text retrieved)
Abstract: In this work, we upgrade the multi-head attention mechanism, the core of the Transformer model, to improve efficiency while maintaining or surpassing the previous accuracy level. We show that multi-head attention can be expressed in the summation form. Drawing on the insight that not all attention heads hold equal significance, we propose Mixture-of-Head attention (MoH), a new architecture that treats attention heads as experts in the Mixture-of-Experts (MoE) mechanism. MoH has two significant advantages: First, MoH enables each token to select the appropriate attention heads, enhancing inference efficiency without compromising accuracy or increasing the number of parameters. Second, MoH replaces the standard summation in multi-head attention with a weighted summation, introducing flexibility to the attention mechanism and unlocking extra performance potential. Extensive experiments on ViT, DiT, and LLMs demonstrate that MoH outperforms multi-head attention by using only 50%-90% of the attention heads. Moreover, we demonstrate that pre-trained multi-head attention models, such as LLaMA3-8B, can be further continue-tuned into our MoH models. Notably, MoH-LLaMA3-8B achieves an average accuracy of 64.0% across 14 benchmarks, outperforming LLaMA3-8B by 2.4% by utilizing only 75% of the attention heads. We believe the proposed MoH is a promising alternative to multi-head attention and provides a strong foundation for developing advanced and efficient attention-based models.
<!-- entry:000083:end -->
<!-- entry:000084:start -->
## [000084] paper — 2026-09-17T10:19:03
arXiv ID: 2507.00698
Title: Rectifying Magnitude Neglect in Linear Attention
Authors: Qihang Fan, Huaibo Huang, Yuang Ai, Ran He
Categories: cs.CV
Published: 2025-07-01T11:49:05+00:00
Local file: papers/raw/2507.00698.md (full text retrieved)
Abstract: As the core operator of Transformers, Softmax Attention exhibits excellent global modeling capabilities. However, its quadratic complexity limits its applicability to vision tasks. In contrast, Linear Attention shares a similar formulation with Softmax Attention while achieving linear complexity, enabling efficient global information modeling. Nevertheless, Linear Attention suffers from a significant performance degradation compared to standard Softmax Attention. In this paper, we analyze the underlying causes of this issue based on the formulation of Linear Attention. We find that, unlike Softmax Attention, Linear Attention entirely disregards the magnitude information of the Query. This prevents the attention score distribution from dynamically adapting as the Query scales. As a result, despite its structural similarity to Softmax Attention, Linear Attention exhibits a significantly different attention score distribution. Based on this observation, we propose Magnitude-Aware Linear Attention (MALA), which modifies the computation of Linear Attention to fully incorporate the Query's magnitude. This adjustment allows MALA to generate an attention score distribution that closely resembles Softmax Attention while exhibiting a more well-balanced structure. We evaluate the effectiveness of MALA on multiple tasks, including image classification, object detection, instance segmentation, semantic segmentation, natural language processing, speech recognition, and image generation. Our MALA achieves strong results on all of these tasks. Code will be available at https://github.com/qhfan/MALA
<!-- entry:000084:end -->
<!-- entry:000085:start -->
## [000085] paper — 2026-09-17T10:19:12
arXiv ID: 2511.20102
Title: SSA: Sparse Sparse Attention by Aligning Full and Sparse Attention Outputs in Feature Space
Authors: Zhenyi Shen, Junru Lu, Lin Gui, Jiazheng Li, Yulan He, Di Yin, Xing Sun
Categories: cs.CL
Published: 2025-11-25T09:21:57+00:00
Local file: papers/raw/2511.20102.md (full text retrieved)
Abstract: Sparse attention reduces the quadratic complexity of full self-attention but faces two challenges: (1) an attention gap, where applying sparse attention to full-attention-trained models causes performance degradation due to train-inference distribution mismatch, and (2) a capability gap, where models trained purely with sparse attention lack complete gradient flow, preventing them from matching full-attention performance. We propose SSA (Sparse Sparse Attention), a training framework that integrates both sparse and full attention with bidirectional attention-output alignment. We prove that the approximation error scales linearly with the attention mass dropped under sparse attention, and show that SSA's alignment objective substantially reduces this quantity compared to baselines. Experiments demonstrate that SSA achieves state-of-the-art performance under both inference modes, adapts smoothly to varying sparsity budgets, and demonstrates superior long-context capabilities.
<!-- entry:000085:end -->
<!-- entry:000086:start -->
## [000086] paper — 2026-09-17T10:19:14
arXiv ID: 2204.00452
Title: Vision Transformer with Cross-attention by Temporal Shift for Efficient Action Recognition
Authors: Ryota Hashiguchi, Toru Tamaki
Categories: cs.CV
Published: 2022-04-01T14:06:19+00:00
Local file: papers/raw/2204.00452.md (full text retrieved)
Abstract: Feature shifts have been shown to be useful for action recognition with CNN-based models since Temporal Shift Module (TSM) was proposed. It is based on frame-wise feature extraction with late fusion, and layer features are shifted along the time direction for the temporal interaction. TokenShift, a recent model based on Vision Transformer (ViT), also uses the temporal feature shift mechanism, which, however, does not fully exploit the structure of Multi-head Self-Attention (MSA) in ViT. In this paper, we propose Multi-head Self/Cross-Attention (MSCA), which fully utilizes the attention structure. TokenShift is based on a frame-wise ViT with features temporally shifted with successive frames (at time t+1 and t-1). In contrast, the proposed MSCA replaces MSA in the frame-wise ViT, and some MSA heads attend to successive frames instead of the current frame. The computation cost is the same as the frame-wise ViT and TokenShift as it simply changes the target to which the attention is taken. There is a choice about which of key, query, and value are taken from the successive frames, then we experimentally compared these variants with Kinetics400. We also investigate other variants in which the proposed MSCA is used along the patch dimension of ViT, instead of the head dimension. Experimental results show that a variant, MSCA-KV, shows the best performance and is better than TokenShift by 0.1% and then ViT by 1.2%.
<!-- entry:000086:end -->
<!-- entry:000087:start -->
## [000087] paper — 2026-09-17T10:19:27
arXiv ID: 2609.04910
Title: Fast Gauss Sums via Flash Attention
Authors: Nicolaj Rux, Sebastian Neumayer
Categories: cs.LG, math.NA
Published: 2026-09-04T09:11:45+00:00
Local file: papers/raw/2609.04910.md (full text retrieved)
Abstract: Gaussian kernel sums are the computational core of maximum mean discrepancies (MMDs), kernel gradient flows, Stein variational gradient descent (SVGD), and many other kernel methods. At the same time, softmax attention has received an extraordinary amount of hardware-aware code engineering, culminating in flash attention. We show that Gauss kernel sums with arbitrary, signed weights can be evaluated via flash attention: two small input augmentations turn the normalized softmax reduction into the unnormalized Gauss sum, without writing a single line of custom GPU code. For feature dimension D>8 in fp16, this approach beats compiled PyTorch code as well as PyKeOps kernels (often significantly) in speed, memory-overhead and accuracy. Indeed, its memory scaling remains linear.
<!-- entry:000087:end -->
<!-- entry:000088:start -->
## [000088] paper — 2026-09-17T10:34:43
arXiv ID: 1811.09575
Title: A Hierarchical Neural Network for Sequence-to-Sequences Learning
Authors: Si Zuo, Zhimin Xu
Categories: cs.CL
Published: 2018-11-23T17:40:30+00:00
Local file: papers/raw/1811.09575.md (full text retrieved)
Abstract: In recent years, the sequence-to-sequence learning neural networks with attention mechanism have achieved great progress. However, there are still challenges, especially for Neural Machine Translation (NMT), such as lower translation quality on long sentences. In this paper, we present a hierarchical deep neural network architecture to improve the quality of long sentences translation. The proposed network embeds sequence-to-sequence neural networks into a two-level category hierarchy by following the coarse-to-fine paradigm. Long sentences are input by splitting them into shorter sequences, which can be well processed by the coarse category network as the long distance dependencies for short sentences is able to be handled by network based on sequence-to-sequence neural network. Then they are concatenated and corrected by the fine category network. The experiments shows that our method can achieve superior results with higher BLEU(Bilingual Evaluation Understudy) scores, lower perplexity and better performance in imitating expression style and words usage than the traditional networks.
<!-- entry:000088:end -->
<!-- entry:000089:start -->
## [000089] paper — 2026-09-17T10:34:55
arXiv ID: 2107.01343
Title: Short-term probabilistic photovoltaic power forecast based on deep convolutional long short-term memory network and kernel density estimation
Authors: Mingliang Bai, Xinyu Zhao, Zhenhua Long, Jinfu Liu, Daren Yu
Categories: cs.LG, eess.SP
Published: 2021-07-03T04:49:24+00:00
Local file: papers/raw/2107.01343.md (full text retrieved)
Abstract: Solar energy is a clean and renewable energy. Photovoltaic (PV) power is an important way to utilize solar energy. Accurate PV power forecast is crucial to the large-scale application of PV power and the stability of electricity grid. This paper proposes a novel method for short-term photovoltaic power forecast using deep convolutional long short-term memory (ConvLSTM) network and kernel density estimation (KDE). In the proposed method, ConvLSTM is used to forecast the future photovoltaic power and KDE is used for estimating the joint probabilistic density function and giving the probabilistic confidence interval. Experiments in an actual photovoltaic power station verify the effectiveness of the proposed method. Comparison experiments with convolutional neural network (CNN) and long short-term memory network (LSTM)shows that ConvLSTM can combine the advantages of both CNN and LSTM and significantly outperform CNN and LSTM in terms of forecast accuracy. Through further comparison with other five conventional methods including multilayer perceptron (MLP), support vector regression (SVR), extreme learning machine (ELM), classification and regression tree (CART) and gradient boosting decision tree (GBDT), ConvLSTM can significantly improve the forecast accuracy by more than 20% for most of the five methods and the superiorities of ConvLSTM are further verified.
<!-- entry:000089:end -->
<!-- entry:000090:start -->
## [000090] paper — 2026-09-17T10:35:02
arXiv ID: 1701.05923
Title: Gate-Variants of Gated Recurrent Unit (GRU) Neural Networks
Authors: Rahul Dey, Fathi M. Salem
Categories: cs.NE, stat.ML
Published: 2017-01-20T20:53:51+00:00
Local file: papers/raw/1701.05923.md (full text retrieved)
Abstract: The paper evaluates three variants of the Gated Recurrent Unit (GRU) in recurrent neural networks (RNN) by reducing parameters in the update and reset gates. We evaluate the three variant GRU models on MNIST and IMDB datasets and show that these GRU-RNN variant models perform as well as the original GRU RNN model while reducing the computational expense.
<!-- entry:000090:end -->
<!-- entry:000091:start -->
## [000091] paper — 2026-09-17T10:35:04
arXiv ID: 1904.04163
Title: Knowledge Distillation For Recurrent Neural Network Language Modeling With Trust Regularization
Authors: Yangyang Shi, Mei-Yuh Hwang, Xin Lei, Haoyu Sheng
Categories: cs.CL
Published: 2019-04-08T16:16:01+00:00
Local file: papers/raw/1904.04163.md (full text retrieved)
Abstract: Recurrent Neural Networks (RNNs) have dominated language modeling because of their superior performance over traditional N-gram based models. In many applications, a large Recurrent Neural Network language model (RNNLM) or an ensemble of several RNNLMs is used. These models have large memory footprints and require heavy computation. In this paper, we examine the effect of applying knowledge distillation in reducing the model size for RNNLMs. In addition, we propose a trust regularization method to improve the knowledge distillation training for RNNLMs. Using knowledge distillation with trust regularization, we reduce the parameter size to a third of that of the previously published best model while maintaining the state-of-the-art perplexity result on Penn Treebank data. In a speech recognition N-bestrescoring task, we reduce the RNNLM model size to 18.5% of the baseline system, with no degradation in word error rate(WER) performance on Wall Street Journal data set.
<!-- entry:000091:end -->
<!-- entry:000092:start -->
## [000092] paper — 2026-09-17T10:35:16
arXiv ID: 2203.00595
Title: Parameter estimation for WMTI-Watson model of white matter using encoder-decoder recurrent neural network
Authors: Yujian Diao, Ileana Ozana Jelescu
Categories: physics.med-ph, cs.LG, physics.bio-ph, q-bio.QM
Published: 2022-03-01T16:33:15+00:00
Local file: papers/raw/2203.00595.md (full text retrieved)
Abstract: Biophysical modelling of the diffusion MRI signal provides estimates of specific microstructural tissue properties. Although nonlinear optimization such as non-linear least squares (NLLS) is the most widespread method for model estimation, it suffers from local minima and high computational cost. Deep Learning approaches are steadily replacing NL fitting, but come with the limitation that the model needs to be retrained for each acquisition protocol and noise level. The White Matter Tract Integrity (WMTI)-Watson model was proposed as an implementation of the Standard Model of diffusion in white matter that estimates model parameters from the diffusion and kurtosis tensors (DKI). Here we proposed a deep learning approach based on the encoder-decoder recurrent neural network (RNN) to increase the robustness and accelerate the parameter estimation of WMTI-Watson. We use an embedding approach to render the model insensitive to potential differences in distributions between training data and experimental data. This RNN-based solver thus has the advantage of being highly efficient in computation and more readily translatable to other datasets, irrespective of acquisition protocol and underlying parameter distributions as long as DKI was pre-computed from the data. In this study, we evaluated the performance of NLLS, the RNN-based method and a multilayer perceptron (MLP) on synthetic and in vivo datasets of rat and human brain. We showed that the proposed RNN-based fitting approach had the advantage of highly reduced computation time over NLLS (from hours to seconds), with similar accuracy and precision but improved robustness, and superior translatability to new datasets over MLP.
<!-- entry:000092:end -->
<!-- entry:000093:start -->
## [000093] paper — 2026-09-17T10:35:26
arXiv ID: 2108.01310
Title: Simulation of Open Quantum Dynamics with Bootstrap-Based Long Short-Term Memory Recurrent Neural Network
Authors: Kunni Lin, Jiawei Peng, Feng Long Gu, Zhenggang Lan
Categories: physics.chem-ph, quant-ph
Published: 2021-08-03T05:58:54+00:00
Local file: papers/raw/2108.01310.md (full text retrieved)
Abstract: The recurrent neural network with the long short-term memory cell (LSTM-NN) is employed to simulate the long-time dynamics of open quantum system. The bootstrap method is applied in the LSTM-NN construction and prediction, which provides a Monte-Carlo estimation of forecasting confidence interval. Within this approach, a large number of LSTM-NNs are constructed by resampling time-series sequences that were obtained from the early-stage quantum evolution given by numerically-exact multilayer multiconfigurational time-dependent Hartree method. The built LSTM-NN ensemble is used for the reliable propagation of the long-time quantum dynamics and the simulated result is highly consistent with the exact evolution. The forecasting uncertainty that partially reflects the reliability of the LSTM-NN prediction is also given. This demonstrates the bootstrap-based LSTM-NN approach is a practical and powerful tool to propagate the long-time quantum dynamics of open systems with high accuracy and low computational cost.
<!-- entry:000093:end -->
<!-- entry:000094:start -->
## [000094] paper — 2026-09-17T10:35:32
arXiv ID: 2008.05575
Title: Comprehensive forecasting based analysis using stacked stateless and stateful Gated Recurrent Unit models
Authors: Swayamjit Saha, Niladri Majumder, Devansh Sangani
Categories: cs.LG, cs.NE
Published: 2020-08-12T21:13:16+00:00
Local file: papers/raw/2008.05575.md (full text retrieved)
Abstract: Photovoltaic power is a renewable source of energy which is highly used in industries. In economically struggling countries it can be a potential source of electric energy as other non-renewable resources are already exhausting. Now if installation of a photovoltaic cell in a region is done prior to research, it may not provide the desired energy output required for running that region. Hence forecasting is required which can elicit the output from a particular region considering its geometrical coordinates, solar parameter like GHI and weather parameters like temperature and wind speed etc. Our paper explores forecasting of solar irradiance on four such regions, out of which three is in West Bengal and one outside to depict with using stacked Gated Recurrent Unit (GRU) models. We have checked that stateful stacked gated recurrent unit model improves the prediction accuracy significantly.
<!-- entry:000094:end -->
<!-- entry:000095:start -->
## [000095] paper — 2026-09-17T10:35:50
arXiv ID: 1611.00196
Title: Recurrent Neural Network Language Model Adaptation Derived Document Vector
Authors: Wei Li, Brian Kan Wing Mak
Categories: cs.CL
Published: 2016-11-01T12:14:02+00:00
Local file: papers/raw/1611.00196.md (full text retrieved)
Abstract: In many natural language processing (NLP) tasks, a document is commonly modeled as a bag of words using the term frequency-inverse document frequency (TF-IDF) vector. One major shortcoming of the frequency-based TF-IDF feature vector is that it ignores word orders that carry syntactic and semantic relationships among the words in a document, and they can be important in some NLP tasks such as genre classification. This paper proposes a novel distributed vector representation of a document: a simple recurrent-neural-network language model (RNN-LM) or a long short-term memory RNN language model (LSTM-LM) is first created from all documents in a task; some of the LM parameters are then adapted by each document, and the adapted parameters are vectorized to represent the document. The new document vectors are labeled as DV-RNN and DV-LSTM respectively. We believe that our new document vectors can capture some high-level sequential information in the documents, which other current document representations fail to capture. The new document vectors were evaluated in the genre classification of documents in three corpora: the Brown Corpus, the BNC Baby Corpus and an artificially created Penn Treebank dataset. Their classification performances are compared with the performance of TF-IDF vector and the state-of-the-art distributed memory model of paragraph vector (PV-DM). The results show that DV-LSTM significantly outperforms TF-IDF and PV-DM in most cases, and combinations of the proposed document vectors with TF-IDF or PV-DM may further improve performance.
<!-- entry:000095:end -->
<!-- entry:000096:start -->
## [000096] paper — 2026-09-17T10:35:53
arXiv ID: 1512.01712
Title: Generating News Headlines with Recurrent Neural Networks
Authors: Konstantin Lopyrev
Categories: cs.CL, cs.LG, cs.NE
Published: 2015-12-05T23:41:22+00:00
Local file: papers/raw/1512.01712.md (full text retrieved)
Abstract: We describe an application of an encoder-decoder recurrent neural network with LSTM units and attention to generating headlines from the text of news articles. We find that the model is quite effective at concisely paraphrasing news articles. Furthermore, we study how the neural network decides which input words to pay attention to, and specifically we identify the function of the different neurons in a simplified attention mechanism. Interestingly, our simplified attention mechanism performs better that the more complex attention mechanism on a held out set of articles.
<!-- entry:000096:end -->
<!-- entry:000097:start -->
## [000097] paper — 2026-09-17T10:36:03
arXiv ID: 2409.08297
Title: Comparative Study of Long Short-Term Memory (LSTM) and Quantum Long Short-Term Memory (QLSTM): Prediction of Stock Market Movement
Authors: Tariq Mahmood, Ibtasam Ahmad, Malik Muhammad Zeeshan Ansar, Jumanah Ahmed Darwish, Rehan Ahmad Khan Sherwani
Categories: q-fin.ST, cs.AI, cs.LG, quant-ph
Published: 2024-09-04T19:34:37+00:00
Local file: papers/raw/2409.08297.md (full text retrieved)
Abstract: In recent years, financial analysts have been trying to develop models to predict the movement of a stock price index. The task becomes challenging in vague economic, social, and political situations like in Pakistan. In this study, we employed efficient models of machine learning such as long short-term memory (LSTM) and quantum long short-term memory (QLSTM) to predict the Karachi Stock Exchange (KSE) 100 index by taking monthly data of twenty-six economic, social, political, and administrative indicators from February 2004 to December 2020. The comparative results of LSTM and QLSTM predicted values of the KSE 100 index with the actual values suggested QLSTM a potential technique to predict stock market trends.
<!-- entry:000097:end -->
<!-- entry:000098:start -->
## [000098] paper — 2026-09-17T10:36:19
arXiv ID: 2412.20171
Title: Geo-ConvGRU: Geographically Masked Convolutional Gated Recurrent Unit for Bird-Eye View Segmentation
Authors: Guanglei Yang, Yongqiang Zhang, Wanlong Li, Yu Tang, Weize Shang, Feng Wen, Hongbo Zhang, Mingli Ding
Categories: cs.CV
Published: 2024-12-28T14:59:48+00:00
Local file: papers/raw/2412.20171.md (full text retrieved)
Abstract: Convolutional Neural Networks (CNNs) have significantly impacted various computer vision tasks, however, they inherently struggle to model long-range dependencies explicitly due to the localized nature of convolution operations. Although Transformers have addressed limitations in long-range dependencies for the spatial dimension, the temporal dimension remains underexplored. In this paper, we first highlight that 3D CNNs exhibit limitations in capturing long-range temporal dependencies. Though Transformers mitigate spatial dimension issues, they result in a considerable increase in parameter and processing speed reduction. To overcome these challenges, we introduce a simple yet effective module, Geographically Masked Convolutional Gated Recurrent Unit (Geo-ConvGRU), tailored for Bird's-Eye View segmentation. Specifically, we substitute the 3D CNN layers with ConvGRU in the temporal module to bolster the capacity of networks for handling temporal dependencies. Additionally, we integrate a geographical mask into the Convolutional Gated Recurrent Unit to suppress noise introduced by the temporal module. Comprehensive experiments conducted on the NuScenes dataset substantiate the merits of the proposed Geo-ConvGRU, revealing that our approach attains state-of-the-art performance in Bird's-Eye View segmentation.
<!-- entry:000098:end -->
<!-- entry:000099:start -->
## [000099] paper — 2026-09-17T10:36:21
arXiv ID: 1506.01192
Title: Personalizing Universal Recurrent Neural Network Language Model with User Characteristic Features by Social Network Crowdsouring
Authors: Bo-Hsiang Tseng, Hung-Yi Lee, Lin-Shan Lee
Categories: cs.CL, cs.LG
Published: 2015-06-03T10:14:21+00:00
Local file: papers/raw/1506.01192.md (full text retrieved)
Abstract: With the popularity of mobile devices, personalized speech recognizer becomes more realizable today and highly attractive. Each mobile device is primarily used by a single user, so it's possible to have a personalized recognizer well matching to the characteristics of individual user. Although acoustic model personalization has been investigated for decades, much less work have been reported on personalizing language model, probably because of the difficulties in collecting enough personalized corpora. Previous work used the corpora collected from social networks to solve the problem, but constructing a personalized model for each user is troublesome. In this paper, we propose a universal recurrent neural network language model with user characteristic features, so all users share the same model, except each with different user characteristic features. These user characteristic features can be obtained by crowdsouring over social networks, which include huge quantity of texts posted by users with known friend relationships, who may share some subject topics and wording patterns. The preliminary experiments on Facebook corpus showed that this proposed approach not only drastically reduced the model perplexity, but offered very good improvement in recognition accuracy in n-best rescoring tests. This approach also mitigated the data sparseness problem for personalized language models.
<!-- entry:000099:end -->
<!-- entry:000100:start -->
## [000100] paper — 2026-09-17T10:36:25
arXiv ID: 1705.06106
Title: Unlabeled Data for Morphological Generation With Character-Based Sequence-to-Sequence Models
Authors: Katharina Kann, Hinrich Schütze
Categories: cs.CL
Published: 2017-05-17T11:48:15+00:00
Local file: papers/raw/1705.06106.md (full text retrieved)
Abstract: We present a semi-supervised way of training a character-based encoder-decoder recurrent neural network for morphological reinflection, the task of generating one inflected word form from another. This is achieved by using unlabeled tokens or random strings as training data for an autoencoding task, adapting a network for morphological reinflection, and performing multi-task training. We thus use limited labeled data more effectively, obtaining up to 9.9% improvement over state-of-the-art baselines for 8 different languages.
<!-- entry:000100:end -->
<!-- entry:000101:start -->
## [000101] paper — 2026-09-17T10:37:46
arXiv ID: 2511.06020
Title: RF-Behavior: A Multimodal Radio-Frequency Dataset for Human Behavior and Emotion Analysis
Authors: Si Zuo, Yuqing Song, Sahar Golipoor, Ying Liu, Xujun Ma, Stephan Sigg
Categories: cs.DB
Published: 2025-11-08T14:21:17+00:00
Local file: papers/raw/2511.06020.md (full text retrieved)
Abstract: Recent research has demonstrated the complementary nature of camera-based and inertial data for modeling human gestures, activities, and sentiment. Yet, despite its growing importance for environmental sensing as well as the advance of joint communication and sensing for prospective WiFi and 6G standards, a dataset that integrates these modalities with radio frequency data (radar and RFID) remains rare. We introduce RF-Behavior, a multimodal radio frequency dataset for comprehensive human behavior and emotion analysis. We collected data from 44 participants performing 21 gestures, 10 activities, and 6 sentiment expressions. Data were captured using synchronized sensors, including 13 radars (8 ground-mounted and 5 ceiling-mounted), 6 to 8 RFID tags (attached to each arm) and LoRa. Inertial measurement units (IMUs) and 24 infrared cameras are used to provide precise motion ground truth. RF-Behavior provides a unified multimodal dataset spanning the full spectrum of human behavior -- from brief gestures to activities and emotional states -- enabling research on multi-task learning across motion and emotion recognition. Benchmark results demonstrate that the strategic sensor placement is complementary across modalities, with distinct performance characteristics across different behavioral categories.
<!-- entry:000101:end -->
<!-- entry:000102:start -->
## [000102] paper — 2026-09-17T10:37:51
arXiv ID: 2408.09191
Title: GSLAMOT: A Tracklet and Query Graph-based Simultaneous Locating, Mapping, and Multiple Object Tracking System
Authors: Shuo Wang, Yongcai Wang, Zhimin Xu, Yongyu Guo, Wanting Li, Zhe Huang, Xuewei Bai, Deying Li
Categories: cs.CV
Published: 2024-08-17T13:09:33+00:00
Local file: papers/raw/2408.09191.md (full text retrieved)
Abstract: For interacting with mobile objects in unfamiliar environments, simultaneously locating, mapping, and tracking the 3D poses of multiple objects are crucially required. This paper proposes a Tracklet Graph and Query Graph-based framework, i.e., GSLAMOT, to address this challenge. GSLAMOT utilizes camera and LiDAR multimodal information as inputs and divides the representation of the dynamic scene into a semantic map for representing the static environment, a trajectory of the ego-agent, and an online maintained Tracklet Graph (TG) for tracking and predicting the 3D poses of the detected mobile objects. A Query Graph (QG) is constructed in each frame by object detection to query and update TG. For accurate object association, a Multi-criteria Star Graph Association (MSGA) method is proposed to find matched objects between the detections in QG and the predicted tracklets in TG. Then, an Object-centric Graph Optimization (OGO) method is proposed to simultaneously optimize the TG, the semantic map, and the agent trajectory. It triangulates the detected objects into the map to enrich the map's semantic information. We address the efficiency issues to handle the three tightly coupled tasks in parallel. Experiments are conducted on KITTI, Waymo, and an emulated Traffic Congestion dataset that highlights challenging scenarios. Experiments show that GSLAMOT enables accurate crowded object tracking while conducting SLAM accurately in challenging scenarios, demonstrating more excellent performances than the state-of-the-art methods. The code and dataset are at https://gslamot.github.io.
<!-- entry:000102:end -->
<!-- entry:000103:start -->
## [000103] paper — 2026-09-17T10:38:21
arXiv ID: 2308.01414
Title: HouYi: An open-source large language model specially designed for renewable energy and carbon neutrality field
Authors: Mingliang Bai, Zhihao Zhou, Ruidong Wang, Yusheng Yang, Zizhen Qin, Yunxiao Chen, Chunjin Mu, Jinfu Liu, Daren Yu
Categories: cs.CL, cs.AI
Published: 2023-07-31T06:59:36+00:00
Local file: papers/raw/2308.01414.md (full text retrieved)
Abstract: Renewable energy is important for achieving carbon neutrality goal. With the great success of Large Language Models (LLMs) like ChatGPT in automatic content generation, LLMs are playing an increasingly important role. However, there has not been a specially designed LLM for renewable energy. Meanwhile, there has not been any dataset of renewable energy for training LLMs. Therefore, this paper published the first open-source Renewable Energy Academic Paper (REAP) dataset for non-commercial LLM research of renewable energy. REAP dataset is collected through searching the title and abstract of 1,168,970 academic literatures from Web of Science. Based on REAP dataset, HouYi model, the first LLM for renewable energy, is developed through finetuning general LLMs. HouYi demonstrated powerful academic paper paragraph generation ability in renewable energy field. Experiments show that its ability to generate academic papers on renewable energy is comparable to ChatGPT, slightly outperforms Claude, ERNIE Bot and SparkDesk, and significantly outperforms open-source LLaMA-13B model.
<!-- entry:000103:end -->
<!-- entry:000104:start -->
## [000104] paper — 2026-09-17T10:38:26
arXiv ID: 1408.2162
Title: Uhrig Dynamical Control of a Three-Level System Via Non-Markovian Quantum State Diffusion
Authors: Wenchong Shu, Xinyu Zhao, Jun Jing, Lian-Ao Wu, Ting Yu
Categories: quant-ph
Published: 2014-08-09T23:09:19+00:00
Local file: papers/raw/1408.2162.md (full text retrieved)
Abstract: In this paper, we use the quantum state diffusion (QSD) equation to implement the Uhrig dynamical decoupling (UDD) to a three-level quantum system coupled to a non-Markovian reservoir comprising of infinite numbers of degrees of freedom. For this purpose, we first reformulate the non-Markovian QSD to incorporate the effect of the external control fields. With this stochastic QSD approach, we demonstrate that an unknown state of the three-level quantum system can be universally protected against both colored phase and amplitude noises when the control-pulse sequences and control operators are properly designed. The advantage of using non-Markovian quantum state diffusion equations is that the control dynamics of open quantum systems can be treated exactly without using Trotter product formula and be efficiently simulated even when the environment comprise of infinite numbers of degrees of freedom. We also show how the control efficacy depends on the environment memory time and the designed time points of applied control pulses.
<!-- entry:000104:end -->
<!-- entry:000105:start -->
## [000105] paper — 2026-09-17T10:38:30
arXiv ID: 2512.03837
Title: Heatmap Pooling Network for Action Recognition from RGB Videos
Authors: Mengyuan Liu, Jinfu Liu, Yongkang Jiang, Bin He
Categories: cs.CV
Published: 2025-12-03T14:36:59+00:00
Local file: papers/raw/2512.03837.md (full text retrieved)
Abstract: Human action recognition (HAR) in videos has garnered widespread attention due to the rich information in RGB videos. Nevertheless, existing methods for extracting deep features from RGB videos face challenges such as information redundancy, susceptibility to noise and high storage costs. To address these issues and fully harness the useful information in videos, we propose a novel heatmap pooling network (HP-Net) for action recognition from videos, which extracts information-rich, robust and concise pooled features of the human body in videos through a feedback pooling module. The extracted pooled features demonstrate obvious performance advantages over the previously obtained pose data and heatmap features from videos. In addition, we design a spatial-motion co-learning module and a text refinement modulation module to integrate the extracted pooled features with other multimodal data, enabling more robust action recognition. Extensive experiments on several benchmarks namely NTU RGB+D 60, NTU RGB+D 120, Toyota-Smarthome and UAV-Human consistently verify the effectiveness of our HP-Net, which outperforms the existing human action recognition methods. Our code is publicly available at: https://github.com/liujf69/HPNet-Action.
<!-- entry:000105:end -->
<!-- entry:000106:start -->
## [000106] paper — 2026-09-17T10:38:36
arXiv ID: 2604.17903
Title: Research on mode transition of micro-newton-level cusped field Hall thruster
Authors: Jiahao Wu, Ming Zeng, Hui Liu, Daren Yu
Categories: physics.plasm-ph
Published: 2026-04-20T07:29:21+00:00
Local file: papers/raw/2604.17903.md (full text retrieved)
Abstract: The micro-newton cusped field Hall thruster is an electric propulsion device that employs microwave-assisted ionization control. It serves as an actuator in drag-free control systems, ensuring control accuracy and stability by providing continuously adjustable thrust over a wide range. However, a mode transition occurring during the regulation process can lead to a sudden change in anode current, degrading control precision and stability. Therefore, it is necessary to investigate the underlying patterns of mode transition. This study examines the variations in internal plasma parameters and discharge characteristics of the thruster before and after microwave mode transition, primarily through probe diagnostics.Experimental results indicate that before the mode transition, the plasma luminous region is primarily concentrated within the electron cyclotron resonance (ECR) area, approximately 1-3 mm upstream of the anode. After the transition, the luminous region moves further upstream, and the plasma density near the anode exceeds the cutoff density, dropping sharply along the axial direction. The fundamental cause of the change in electron heating mechanism is the alteration in the propagation characteristics of fundamental waves due to this plasma density variation.When the plasma density rises to the cutoff density, the R wave and O wave, which drive ionization, are rapidly attenuated or reflected. At this point, the R-wave cannot reach the resonance layer, causing the dominant ECR ionization to become ineffective. The ionization mechanism shifts from being dominated by the R wave and O wave to being dominated primarily by the O wave. Consequently, the electron heating mechanism transitions from volume heating to surface wave heating......
<!-- entry:000106:end -->
<!-- entry:000107:start -->
## [000107] paper — 2026-09-17T10:39:05
arXiv ID: 2112.00879
Title: Generating Diverse 3D Reconstructions from a Single Occluded Face Image
Authors: Rahul Dey, Vishnu Naresh Boddeti
Categories: cs.CV
Published: 2021-12-01T23:13:49+00:00
Local file: papers/raw/2112.00879.md (full text retrieved)
Abstract: Occlusions are a common occurrence in unconstrained face images. Single image 3D reconstruction from such face images often suffers from corruption due to the presence of occlusions. Furthermore, while a plurality of 3D reconstructions is plausible in the occluded regions, existing approaches are limited to generating only a single solution. To address both of these challenges, we present Diverse3DFace, which is specifically designed to simultaneously generate a diverse and realistic set of 3D reconstructions from a single occluded face image. It consists of three components: a global+local shape fitting process, a graph neural network-based mesh VAE, and a Determinantal Point Process based diversity promoting iterative optimization procedure. Quantitative and qualitative comparisons of 3D reconstruction on occluded faces show that Diverse3DFace can estimate 3D shapes that are consistent with the visible regions in the target image while exhibiting high, yet realistic, levels of diversity on the occluded regions. On face images occluded by masks, glasses, and other random objects, Diverse3DFace generates a distribution of 3D shapes having ~50% higher diversity on the occluded regions compared to the baselines. Moreover, our closest sample to the ground truth has ~40% lower MSE than the singular reconstructions by existing approaches.
<!-- entry:000107:end -->
<!-- entry:000108:start -->
## [000108] paper — 2026-09-17T10:39:07
arXiv ID: 1712.00006
Title: Comparing Deep Reinforcement Learning and Evolutionary Methods in Continuous Control
Authors: Shangtong Zhang, Osmar R. Zaiane
Categories: cs.LG, cs.AI
Published: 2017-11-30T03:40:06+00:00
Local file: papers/raw/1712.00006.md (full text retrieved)
Abstract: Reinforcement Learning and the Evolutionary Strategy are two major approaches in addressing complicated control problems. Both are strong contenders and have their own devotee communities. Both groups have been very active in developing new advances in their own domain and devising, in recent years, leading-edge techniques to address complex continuous control tasks. Here, in the context of Deep Reinforcement Learning, we formulate a parallelized version of the Proximal Policy Optimization method and a Deep Deterministic Policy Gradient method. Moreover, we conduct a thorough comparison between the state-of-the-art techniques in both camps fro continuous control; evolutionary methods and Deep Reinforcement Learning methods. The results show there is no consistent winner.
<!-- entry:000108:end -->
<!-- entry:000109:start -->
## [000109] paper — 2026-09-17T10:39:14
arXiv ID: 1812.01943
Title: Prediction of typhoon tracks using a generative adversarial network with observational and meteorological data
Authors: Mario Rüttgers, Sangseung Lee, Donghyun You
Categories: physics.ao-ph
Published: 2018-12-05T12:06:22+00:00
Local file: papers/raw/1812.01943.md (full text retrieved)
Abstract: Tracks of typhoons are predicted using a generative adversarial network (GAN) with observational data in form of satellite images and meteorological data from a reanalysis database. Time series of images of typhoons which occurred in the Korean Peninsula in the past are used to train the neural network. The trained GAN is employed to produce a 6-hour-advance track of a typhoon for which the GAN was not trained. The predicted image favorably identifies the future location of the typhoon center as well as the deformed cloud structures. The errors between predicted and real typhoon centers are measured quantitatively in kilometers. 65.5 % of all typhoon center predictions have an error of less than 80 km, 31.5 % lie within a range of 80 - 120 km and the remaining 3.0 % are above 120 km. The overall error is 67.2 km, compared to 95.6 km when only observational data are used as input. The cloud structure prediction is evaluated qualitatively. It is shown that the GAN is able to predict trends in cloud motion. It is found that adding physically meaningful meteorological data to satellite images improves the sharpness of predicted images.
<!-- entry:000109:end -->
<!-- entry:000110:start -->
## [000110] paper — 2026-09-17T10:39:28
arXiv ID: 2110.08079
Title: Automated Quality Control of Vacuum Insulated Glazing by Convolutional Neural Network Image Classification
Authors: Henrik Riedel, Sleheddine Mokdad, Isabell Schulz, Cenk Kocer, Philipp Rosendahl, Jens Schneider, Michael A. Kraus, Michael Drass
Categories: cs.CV, cs.AI
Published: 2021-10-15T13:10:54+00:00
Local file: papers/raw/2110.08079.md (full text retrieved)
Abstract: Vacuum Insulated Glazing (VIG) is a highly thermally insulating window technology, which boasts an extremely thin profile and lower weight as compared to gas-filled insulated glazing units of equivalent performance. The VIG is a double-pane configuration with a submillimeter vacuum gap between the panes and therefore under constant atmospheric pressure over their service life. Small pillars are positioned between the panes to maintain the gap, which can damage the glass reducing the lifetime of the VIG unit. To efficiently assess any surface damage on the glass, an automated damage detection system is highly desirable. For the purpose of classifying the damage, we have developed, trained, and tested a deep learning computer vision system using convolutional neural networks. The classification model flawlessly classified the test dataset with an area under the curve (AUC) for the receiver operating characteristic (ROC) of 100%. We have automatically cropped the images down to their relevant information by using Faster-RCNN to locate the position of the pillars. We employ the state-of-the-art methods Grad-CAM and Score-CAM of explainable Artificial Intelligence (XAI) to provide an understanding of the internal mechanisms and were able to show that our classifier outperforms ResNet50V2 for identification of crack locations and geometry. The proposed methods can therefore be used to detect systematic defects even without large amounts of training data. Further analyses of our model's predictive capabilities demonstrates its superiority over state-of-the-art models (ResNet50V2, ResNet101V2 and ResNet152V2) in terms of convergence speed, accuracy, precision at 100% recall and AUC for ROC.
<!-- entry:000110:end -->
<!-- entry:000111:start -->
## [000111] paper — 2026-09-17T10:39:31
arXiv ID: 2408.06717
Title: Proficient Graph Neural Network Design by Accumulating Knowledge on Large Language Models
Authors: Jialiang Wang, Hanmo Liu, Shimin Di, Zhili Wang, Jiachuan Wang, Lei Chen, Xiaofang Zhou
Categories: cs.LG, cs.AI
Published: 2024-08-13T08:22:01+00:00
Local file: papers/raw/2408.06717.md (full text retrieved)
Abstract: High-level automation is increasingly critical in AI, driven by rapid advances in large language models (LLMs) and AI agents. However, LLMs, despite their general reasoning power, struggle significantly in specialized, data-sensitive tasks such as designing Graph Neural Networks (GNNs). This difficulty arises from (1) the inherent knowledge gaps in modeling the intricate, varying relationships between graph properties and suitable architectures and (2) the external noise from misleading descriptive inputs, often resulting in generic or even misleading model suggestions. Achieving proficiency in designing data-aware models -- defined as the meta-level capability to systematically accumulate, interpret, and apply data-specific design knowledge -- remains challenging for existing automated approaches, due to their inefficient construction and application of meta-knowledge. To achieve meta-level proficiency, we propose DesiGNN, a knowledge-centered framework that systematically converts past model design experience into structured, fine-grained knowledge priors well-suited for meta-learning with LLMs. To account for the inherent variability and external noise, DesiGNN aligns empirical property filtering from extensive benchmarks with adaptive elicitation of literature insights via LLMs. By constructing a solid meta-knowledge between unseen graph understanding and known effective architecture patterns, DesiGNN can deliver top-5.77% initial model proposals for unseen datasets within seconds and achieve consistently superior performance with minimal search cost compared to baselines.
<!-- entry:000111:end -->
<!-- entry:000112:start -->
## [000112] paper — 2026-09-17T10:39:35
arXiv ID: 1708.07012
Title: Variational autoencoders for tissue heterogeneity exploration from (almost) no preprocessed mass spectrometry imaging data
Authors: Paolo Inglese, James L. Alexander, Anna Mroz, Zoltan Takats, Robert Glen
Categories: q-bio.QM, cs.LG, stat.ML
Published: 2017-08-23T14:12:53+00:00
Local file: papers/raw/1708.07012.md (full text retrieved)
Abstract: The paper presents the application of Variational Autoencoders (VAE) for data dimensionality reduction and explorative analysis of mass spectrometry imaging data (MSI). The results confirm that VAEs are capable of detecting the patterns associated with the different tissue sub-types with performance than standard approaches.
<!-- entry:000112:end -->
<!-- entry:000113:start -->
## [000113] paper — 2026-09-17T10:39:37
arXiv ID: 2505.03377
Title: Gene finding revisited: improved robustness through structured decoding from learned embeddings
Authors: Frederikke I. Marin, Dennis Pultz, Wouter Boomsma
Categories: q-bio.GN
Published: 2025-05-06T09:53:15+00:00
Local file: papers/raw/2505.03377.md (full text retrieved)
Abstract: Gene finding is the task of identifying the locations of coding sequences within the vast amount of genetic code contained in the genome. With an ever increasing quantity of raw genome sequences, gene finding is an important avenue towards understanding the genetic information of (novel) organisms, as well as learning shared patterns across evolutionarily diverse species. The current state of the art are graphical models usually trained per organism and requiring manually curated datasets. However, these models lack the flexibility to incorporate deep learning representation learning techniques that have in recent years been transformative in the analysis of pro tein sequences, and which could potentially help gene finders exploit the growing number of the sequenced genomes to expand performance across multiple organisms. Here, we propose a novel approach, combining learned embeddings of raw genetic sequences with exact decoding using a latent conditional random field. We show that the model achieves performance matching the current state of the art, while increasing training robustness, and removing the need for manually fitted length distributions. As language models for DNA improve, this paves the way for more performant cross-organism gene-finders.
<!-- entry:000113:end -->
<!-- entry:000114:start -->
## [000114] paper — 2026-09-17T10:39:41
arXiv ID: 2602.07139
Title: ImmCOGNITO: Identity Obfuscation in Millimeter-Wave Radar-Based Gesture Recognition for IoT Environments
Authors: Ying Liu, Si Zuo, Chao Yang, Yuqing Song, Dariush Salami, Stephan Sigg
Categories: cs.HC
Published: 2026-02-06T19:26:33+00:00
Local file: papers/raw/2602.07139.md (full text retrieved)
Abstract: Millimeter-Wave (mmWave) radar enables camera-free gesture recognition for Internet of Things (IoT) interfaces, with robustness to lighting variations and partial occlusions. However, recent studies reveal that its data can inadvertently encode biometric signatures, raising critical privacy challenges for IoT applications. In particular, we demonstrate that mmWave radar point cloud data can leak identity-related information in the absence of explicit identity labels. To address this risk, we propose {ImmCOGNITO}, a graph-based autoencoder that transforms radar gesture point clouds to preserve gesture-relevant structure while suppressing identity cues. The encoder first constructs a directed graph for each sequence using Temporal Graph KNN. Edges are defined to capture inter-frame temporal dynamics. A message-passing neural network with multi-head self-attention then aggregates local and global spatio-temporal context, and the global max-pooled feature is concatenated with the original features. The decoder then reconstructs a minimally perturbed point cloud that retains gesture discriminative attributes while achieving de-identification. Training jointly optimizes reconstruction, gesture-preservation, and de-identification objectives. Evaluations on two public datasets, PantoRad and MHomeGes, show that ImmCOGNITO substantially reduces identification accuracy while maintaining high gesture recognition performance.
<!-- entry:000114:end -->
<!-- entry:000115:start -->
## [000115] paper — 2026-09-17T10:40:11
arXiv ID: 2508.03590
Title: SolarSeer: Ultrafast and accurate 24-hour solar irradiance forecasts outperforming numerical weather prediction across the USA
Authors: Mingliang Bai, Zuliang Fang, Shengyu Tao, Siqi Xiang, Jiang Bian, Yanfei Xiang, Pengcheng Zhao, Weixin Jin, Jonathan A. Weyn, Haiyu Dong, Bin Zhang, Hongyu Sun, Kit Thambiratnam, Qi Zhang, Hongbin Sun, Xuan Zhang, Qiuwei Wu
Categories: cs.LG, cs.CE
Published: 2025-08-05T15:57:22+00:00
Local file: papers/raw/2508.03590.md (full text retrieved)
Abstract: Accurate 24-hour solar irradiance forecasting is essential for the safe and economic operation of solar photovoltaic systems. Traditional numerical weather prediction (NWP) models represent the state-of-the-art in forecasting performance but rely on computationally costly data assimilation and solving complicated partial differential equations (PDEs) that simulate atmospheric physics. Here, we introduce SolarSeer, an end-to-end large artificial intelligence (AI) model for solar irradiance forecasting across the Contiguous United States (CONUS). SolarSeer is designed to directly map the historical satellite observations to future forecasts, eliminating the computational overhead of data assimilation and PDEs solving. This efficiency allows SolarSeer to operate over 1,500 times faster than traditional NWP, generating 24-hour cloud cover and solar irradiance forecasts for the CONUS at 5-kilometer resolution in under 3 seconds. Compared with the state-of-the-art NWP in the CONUS, i.e., High-Resolution Rapid Refresh (HRRR), SolarSeer significantly reduces the root mean squared error of solar irradiance forecasting by 27.28% in reanalysis data and 15.35% across 1,800 stations. SolarSeer also effectively captures solar irradiance fluctuations and significantly enhances the first-order irradiance difference forecasting accuracy. SolarSeer's ultrafast, accurate 24-hour solar irradiance forecasts provide strong support for the transition to sustainable, net-zero energy systems.
<!-- entry:000115:end -->
<!-- entry:000116:start -->
## [000116] paper — 2026-09-17T10:40:14
arXiv ID: 1503.00014
Title: Phonon mediated spin relaxation in a moving quantum dot: Doppler shift, Cherenkov radiation, and spin relaxation boom
Authors: Xinyu Zhao, Peihao Huang, Xuedong Hu
Categories: cond-mat.mes-hall, quant-ph
Published: 2015-02-27T21:09:57+00:00
Local file: papers/raw/1503.00014.md (full text retrieved)
Abstract: We study relaxation of a moving spin qubit caused by phonon noise. As we vary the speed of the qubit, we observe several interesting features in spin relaxation and the associated phonon emission, induced by Doppler effect. In particular, in the supersonic regime, the phonons emitted by the relaxing qubit is concentrated along certain directions, similar to the shock waves produced in classical Cherenkov effect. As the speed of the moving qubit increases from the subsonic regime to the supersonic regime, the qubit experiences a peak in the spin relaxation rate near the speed of sound, which we term a spin relaxation boom in analogy to the classical sonic boom. We also find that the moving spin qubit may have a lower relaxation rate than a static qubit, which hints at the possibility of coherence-preserving transportation for a spin qubit. While the physics we have studied here has strong classical analogies, we do find that quantum confinement for the spin qubit plays an important role in all the phenomena we observe. Specifically, it produces a correction on the Cherenkov angle, and removes the divergence in relaxation rate at the sonic barrier. It is our hope that our results would encourage further research into approaches for transferring and preserving quantum information in spin qubit architectures.
<!-- entry:000116:end -->
<!-- entry:000117:start -->
## [000117] paper — 2026-09-17T10:40:17
arXiv ID: 2404.15719
Title: HDBN: A Novel Hybrid Dual-branch Network for Robust Skeleton-based Action Recognition
Authors: Jinfu Liu, Baiqiao Yin, Jiaying Lin, Jiajun Wen, Yue Li, Mengyuan Liu
Categories: cs.CV, cs.AI
Published: 2024-04-24T08:11:50+00:00
Local file: papers/raw/2404.15719.md (full text retrieved)
Abstract: Skeleton-based action recognition has gained considerable traction thanks to its utilization of succinct and robust skeletal representations. Nonetheless, current methodologies often lean towards utilizing a solitary backbone to model skeleton modality, which can be limited by inherent flaws in the network backbone. To address this and fully leverage the complementary characteristics of various network architectures, we propose a novel Hybrid Dual-Branch Network (HDBN) for robust skeleton-based action recognition, which benefits from the graph convolutional network's proficiency in handling graph-structured data and the powerful modeling capabilities of Transformers for global information. In detail, our proposed HDBN is divided into two trunk branches: MixGCN and MixFormer. The two branches utilize GCNs and Transformers to model both 2D and 3D skeletal modalities respectively. Our proposed HDBN emerged as one of the top solutions in the Multi-Modal Video Reasoning and Analyzing Competition (MMVRAC) of 2024 ICME Grand Challenge, achieving accuracies of 47.95% and 75.36% on two benchmarks of the UAV-Human dataset by outperforming most existing methods. Our code will be publicly available at: https://github.com/liujf69/ICMEW2024-Track10.
<!-- entry:000117:end -->
<!-- entry:000118:start -->
## [000118] paper — 2026-09-17T10:40:31
arXiv ID: 2504.19712
Title: The effect of ion rotational flow on Hall thruster azimuthal instability via two dimensional PIC simulations
Authors: Zhijun Zhou, Lihuan Xie, Xin Luo, Yinjian Zhao, Daren Yu
Categories: physics.plasm-ph
Published: 2025-04-28T12:06:17+00:00
Local file: papers/raw/2504.19712.md (full text retrieved)
Abstract: Previous experimental studies have found that the neutral gas rotational flow in the opposite direction of electron Hall drift can lead to better experimental results comparing to the same direction. In Hall thrusters, the core factor influencing operational states is the electron cross field transport, where the azimuthal instability serves as a key mechanism. The rotational flow of neutral gas may affect instability by altering initial azimuthal velocity of ions, which has not been investigated before. Therefore, to study the effects of ion rotational flow of varying magnitudes and directions on azimuthal instability, simulations are conducted in this work based on two benchmark particle-in-cell (PIC) cases: the azimuthal-axial and the azimuthal-radial. The results indicate that the ion rotational flow velocity can potentially complicate the coupling characteristics of the electron cyclotron drifting instability and the modified two stream instability, particularly when a reverse rotational flow velocity is added. In general, both co-directional and reverse ion rotational flow have been observed to inhibit azimuthal instability, which results in a decrease in axial electron mobility. A 1% addition of the ion rotational flow (compared to the electron drift) would result in a 10% change of the electron mobility due to varied azimuthal instability, and the decrease in electron mobility of the reverse ion rotational flow is greater than that of co-directional. In addition, detailed spectral analyses are carried out to study the relation between ECDI, MTSI, and resonant wave-wave interactions.
<!-- entry:000118:end -->
<!-- entry:000119:start -->
## [000119] paper — 2026-09-17T10:41:15
arXiv ID: 2110.10395
Title: 3DFaceFill: An Analysis-By-Synthesis Approach to Face Completion
Authors: Rahul Dey, Vishnu Boddeti
Categories: cs.CV
Published: 2021-10-20T06:31:47+00:00
Local file: papers/raw/2110.10395.md (full text retrieved)
Abstract: Existing face completion solutions are primarily driven by end-to-end models that directly generate 2D completions of 2D masked faces. By having to implicitly account for geometric and photometric variations in facial shape and appearance, such approaches result in unrealistic completions, especially under large variations in pose, shape, illumination and mask sizes. To alleviate these limitations, we introduce 3DFaceFill, an analysis-by-synthesis approach for face completion that explicitly considers the image formation process. It comprises three components, (1) an encoder that disentangles the face into its constituent 3D mesh, 3D pose, illumination and albedo factors, (2) an autoencoder that inpaints the UV representation of facial albedo, and (3) a renderer that resynthesizes the completed face. By operating on the UV representation, 3DFaceFill affords the power of correspondence and allows us to naturally enforce geometrical priors (e.g. facial symmetry) more effectively. Quantitatively, 3DFaceFill improves the state-of-the-art by up to 4dB higher PSNR and 25% better LPIPS for large masks. And, qualitatively, it leads to demonstrably more photorealistic face completions over a range of masks and occlusions while preserving consistency in global and component-wise shape, pose, illumination and eye-gaze.
<!-- entry:000119:end -->
<!-- entry:000120:start -->
## [000120] paper — 2026-09-17T10:41:18
arXiv ID: 1701.07274
Title: Deep Reinforcement Learning: An Overview
Authors: Yuxi Li
Categories: cs.LG
Published: 2017-01-25T11:52:11+00:00
Local file: papers/raw/1701.07274.md (full text retrieved)
Abstract: We give an overview of recent exciting achievements of deep reinforcement learning (RL). We discuss six core elements, six important mechanisms, and twelve applications. We start with background of machine learning, deep learning and reinforcement learning. Next we discuss core RL elements, including value function, in particular, Deep Q-Network (DQN), policy, reward, model, planning, and exploration. After that, we discuss important mechanisms for RL, including attention and memory, unsupervised learning, transfer learning, multi-agent RL, hierarchical RL, and learning to learn. Then we discuss various applications of RL, including games, in particular, AlphaGo, robotics, natural language processing, including dialogue systems, machine translation, and text generation, computer vision, neural architecture design, business management, finance, healthcare, Industry 4.0, smart grid, intelligent transportation systems, and computer systems. We mention topics not reviewed yet, and list a collection of RL resources. After presenting a brief summary, we close with discussions.   Please see Deep Reinforcement Learning, arXiv:1810.06339, for a significant update.
<!-- entry:000120:end -->
<!-- entry:000121:start -->
## [000121] paper — 2026-09-17T13:58:31
arXiv ID: 1808.03570
Title: Densely Connected Convolutional Networks for Speech Recognition
Authors: Chia Yu Li, Ngoc Thang Vu
Categories: cs.CL
Published: 2018-08-10T14:54:10+00:00
Local file: papers/raw/1808.03570.md (full text retrieved)
Abstract: This paper presents our latest investigation on Densely Connected Convolutional Networks (DenseNets) for acoustic modelling (AM) in automatic speech recognition. DenseN-ets are very deep, compact convolutional neural networks, which have demonstrated incredible improvements over the state-of-the-art results on several data sets in computer vision. Our experimental results show that DenseNet can be used for AM significantly outperforming other neural-based models such as DNNs, CNNs, VGGs. Furthermore, results on Wall Street Journal revealed that with only a half of the training data DenseNet was able to outperform other models trained with the full data set by a large margin.
<!-- entry:000121:end -->
<!-- entry:000122:start -->
## [000122] paper — 2026-09-17T13:58:36
arXiv ID: 2407.08469
Title: A Comprehensive Convolutional Neural Network Architecture Design using Magnetic Skyrmion and Domain Wall
Authors: Saumya Gupta, Venkatesh Vadde, Bhaskaran Muralidharan, Abhishek Sharma
Categories: cond-mat.mes-hall
Published: 2024-07-11T13:04:02+00:00
Local file: papers/raw/2407.08469.md (full text retrieved)
Abstract: Spintronic-based neuromorphic hardware offers high-density and rapid data processing at nanoscale lengths by leveraging magnetic configurations like skyrmion and domain walls. Here, we present the maximal hardware implementation of a convolutional neural network (CNN) based on a compact multi-bit skyrmion-based synapse and a hybrid CMOS domain wall-based circuit for activation and max-pooling functionalities. We demonstrate the micromagnetic design and operation of a circular bilayer skyrmion system mimicking a scalable artificial synapse, demonstrated up to 6-bit (64 states) with an ultra-low energy consumption of 0.87 fJ per state update. We further show that the synaptic weight modulation is achieved by the perpendicular current interaction with the labyrinth-maze like uniaxial anisotropy profile, inducing skyrmionic gyration, thereby enabling long-term potentiation (LTP) and long-term depression (LTD) operations. Furthermore, we present a simultaneous rectified linear (ReLU) activation and max pooling circuitry featuring a SOT-based domain wall ReLU with a power consumption of 4.73 $μ$W. The ReLU function, stabilized by a parabolic uniaxial anisotropy profile, encodes domain wall positions into continuous resistance states coupled with the HSPICE circuit simulator. Our integrated skyrmion and domain wall-based spintronic hardware achieves 98.07% accuracy in convolutional neural network (CNN) based pattern recognition task, consuming 110 mW per image.
<!-- entry:000122:end -->
<!-- entry:000123:start -->
## [000123] paper — 2026-09-17T13:58:39
arXiv ID: 1807.06521
Title: CBAM: Convolutional Block Attention Module
Authors: Sanghyun Woo, Jongchan Park, Joon-Young Lee, In So Kweon
Categories: cs.CV
Published: 2018-07-17T16:05:59+00:00
Local file: papers/raw/1807.06521.md (full text retrieved)
Abstract: We propose Convolutional Block Attention Module (CBAM), a simple yet effective attention module for feed-forward convolutional neural networks. Given an intermediate feature map, our module sequentially infers attention maps along two separate dimensions, channel and spatial, then the attention maps are multiplied to the input feature map for adaptive feature refinement. Because CBAM is a lightweight and general module, it can be integrated into any CNN architectures seamlessly with negligible overheads and is end-to-end trainable along with base CNNs. We validate our CBAM through extensive experiments on ImageNet-1K, MS~COCO detection, and VOC~2007 detection datasets. Our experiments show consistent improvements in classification and detection performances with various models, demonstrating the wide applicability of CBAM. The code and models will be publicly available.
<!-- entry:000123:end -->
<!-- entry:000124:start -->
## [000124] paper — 2026-09-17T13:58:43
arXiv ID: 2308.13343
Title: Squeeze aggregated excitation network
Authors: Mahendran N
Categories: cs.CV, cs.AI
Published: 2023-08-25T12:30:48+00:00
Local file: papers/raw/2308.13343.md (full text retrieved)
Abstract: Convolutional neural networks have spatial representations which read patterns in the vision tasks. Squeeze and excitation links the channel wise representations by explicitly modeling on channel level. Multi layer perceptrons learn global representations and in most of the models it is used often at the end after all convolutional layers to gather all the information learned before classification. We propose a method of inducing the global representations within channels to have better performance of the model. We propose SaEnet, Squeeze aggregated excitation network, for learning global channelwise representation in between layers. The proposed module takes advantage of passing important information after squeeze by having aggregated excitation before regaining its shape. We also introduce a new idea of having a multibranch linear(dense) layer in the network. This learns global representations from the condensed information which enhances the representational power of the network. The proposed module have undergone extensive experiments by using Imagenet and CIFAR100 datasets and compared with closely related architectures. The analyzes results that proposed models outputs are comparable and in some cases better than existing state of the art architectures.
<!-- entry:000124:end -->
<!-- entry:000125:start -->
## [000125] paper — 2026-09-17T13:58:46
arXiv ID: 2112.10085
Title: D-HAN: Dynamic News Recommendation with Hierarchical Attention Network
Authors: Qinghua Zhao
Categories: cs.IR, cs.AI
Published: 2021-12-19T08:11:57+00:00
Local file: papers/raw/2112.10085.md (full text retrieved)
Abstract: News recommendation models often fall short in capturing users' preferences due to their static approach to user-news interactions. To address this limitation, we present a novel dynamic news recommender model that seamlessly integrates continuous time information to a hierarchical attention network that effectively represents news information at the sentence, element, and sequence levels. Moreover, we introduce a dynamic negative sampling method to optimize users' implicit feedback. To validate our model's effectiveness, we conduct extensive experiments on three real-world datasets. The results demonstrate the effectiveness of our proposed approach.
<!-- entry:000125:end -->
<!-- entry:000126:start -->
## [000126] paper — 2026-09-17T13:58:48
arXiv ID: 2410.03805
Title: Local Attention Mechanism: Boosting the Transformer Architecture for Long-Sequence Time Series Forecasting
Authors: Ignacio Aguilera-Martos, Andrés Herrera-Poyatos, Julián Luengo, Francisco Herrera
Categories: cs.LG
Published: 2024-10-04T11:32:02+00:00
Local file: papers/raw/2410.03805.md (full text retrieved)
Abstract: Transformers have become the leading choice in natural language processing over other deep learning architectures. This trend has also permeated the field of time series analysis, especially for long-horizon forecasting, showcasing promising results both in performance and running time.   In this paper, we introduce Local Attention Mechanism (LAM), an efficient attention mechanism tailored for time series analysis. This mechanism exploits the continuity properties of time series to reduce the number of attention scores computed. We present an algorithm for implementing LAM in tensor algebra that runs in time and memory O(nlogn), significantly improving upon the O(n^2) time and memory complexity of traditional attention mechanisms. We also note the lack of proper datasets to evaluate long-horizon forecast models. Thus, we propose a novel set of datasets to improve the evaluation of models addressing long-horizon forecasting challenges.   Our experimental analysis demonstrates that the vanilla transformer architecture magnified with LAM surpasses state-of-the-art models, including the vanilla attention mechanism. These results confirm the effectiveness of our approach and highlight a range of future challenges in long-sequence time series forecasting.
<!-- entry:000126:end -->
<!-- entry:000127:start -->
## [000127] paper — 2026-09-17T13:58:51
arXiv ID: 2112.10108
Title: Investigation of Densely Connected Convolutional Networks with Domain Adversarial Learning for Noise Robust Speech Recognition
Authors: Chia Yu Li, Ngoc Thang Vu
Categories: cs.CL, cs.LG, eess.AS
Published: 2021-12-19T10:29:17+00:00
Local file: papers/raw/2112.10108.md (full text retrieved)
Abstract: We investigate densely connected convolutional networks (DenseNets) and their extension with domain adversarial training for noise robust speech recognition. DenseNets are very deep, compact convolutional neural networks which have demonstrated incredible improvements over the state-of-the-art results in computer vision. Our experimental results reveal that DenseNets are more robust against noise than other neural network based models such as deep feed forward neural networks and convolutional neural networks. Moreover, domain adversarial learning can further improve the robustness of DenseNets against both, known and unknown noise conditions.
<!-- entry:000127:end -->
<!-- entry:000128:start -->
## [000128] paper — 2026-09-17T13:58:54
arXiv ID: 2309.03530
Title: Efficient Single Object Detection on Image Patches with Early Exit Enhanced High-Precision CNNs
Authors: Arne Moos
Categories: cs.CV, cs.LG, cs.RO
Published: 2023-09-07T07:23:55+00:00
Local file: papers/raw/2309.03530.md (full text retrieved)
Abstract: This paper proposes a novel approach for detecting objects using mobile robots in the context of the RoboCup Standard Platform League, with a primary focus on detecting the ball. The challenge lies in detecting a dynamic object in varying lighting conditions and blurred images caused by fast movements. To address this challenge, the paper presents a convolutional neural network architecture designed specifically for computationally constrained robotic platforms. The proposed CNN is trained to achieve high precision classification of single objects in image patches and to determine their precise spatial positions. The paper further integrates Early Exits into the existing high-precision CNN architecture to reduce the computational cost of easily rejectable cases in the background class. The training process involves a composite loss function based on confidence and positional losses with dynamic weighting and data augmentation. The proposed approach achieves a precision of 100% on the validation dataset and a recall of almost 87%, while maintaining an execution time of around 170 $μ$s per hypotheses. By combining the proposed approach with an Early Exit, a runtime optimization of more than 28%, on average, can be achieved compared to the original CNN. Overall, this paper provides an efficient solution for an enhanced detection of objects, especially the ball, in computationally constrained robotic platforms.
<!-- entry:000128:end -->
<!-- entry:000129:start -->
## [000129] paper — 2026-09-17T13:58:58
arXiv ID: 2202.06673
Title: Convolutional Neural Network with Convolutional Block Attention Module for Finger Vein Recognition
Authors: Zhongxia Zhang, Mingwen Wang
Categories: cs.CV
Published: 2022-02-14T12:59:23+00:00
Local file: papers/raw/2202.06673.md (full text retrieved)
Abstract: Convolutional neural networks have become a popular research in the field of finger vein recognition because of their powerful image feature representation. However, most researchers focus on improving the performance of the network by increasing the CNN depth and width, which often requires high computational effort. Moreover, we can notice that not only the importance of pixels in different channels is different, but also the importance of pixels in different positions of the same channel is different. To reduce the computational effort and to take into account the different importance of pixels, we propose a lightweight convolutional neural network with a convolutional block attention module (CBAM) for finger vein recognition, which can achieve a more accurate capture of visual structures through an attention mechanism. First, image sequences are fed into a lightweight convolutional neural network we designed to improve visual features. Afterwards, it learns to assign feature weights in an adaptive manner with the help of a convolutional block attention module. The experiments are carried out on two publicly available databases and the results demonstrate that the proposed method achieves a stable, highly accurate, and robust performance in multimodal finger recognition.
<!-- entry:000129:end -->
<!-- entry:000130:start -->
## [000130] paper — 2026-09-17T13:59:04
arXiv ID: 2305.00088
Title: DD-CISENet: Dual-Domain Cross-Iteration Squeeze and Excitation Network for Accelerated MRI Reconstruction
Authors: Xiongchao Chen, Zhigang Peng, Gerardo Hermosillo Valadez
Categories: eess.IV, cs.CV
Published: 2023-04-28T20:44:48+00:00
Local file: papers/raw/2305.00088.md (full text retrieved)
Abstract: Magnetic resonance imaging (MRI) is widely employed for diagnostic tests in neurology. However, the utility of MRI is largely limited by its long acquisition time. Acquiring fewer k-space data in a sparse manner is a potential solution to reducing the acquisition time, but it can lead to severe aliasing reconstruction artifacts. In this paper, we present a novel Dual-Domain Cross-Iteration Squeeze and Excitation Network (DD-CISENet) for accelerated sparse MRI reconstruction. The information of k-spaces and MRI images can be iteratively fused and maintained using the Cross-Iteration Residual connection (CIR) structures. This study included 720 multi-coil brain MRI cases adopted from the open-source fastMRI Dataset. Results showed that the average reconstruction error by DD-CISENet was 2.28 $\pm$ 0.57%, which outperformed existing deep learning methods including image-domain prediction (6.03 $\pm$ 1.31, p < 0.001), k-space synthesis (6.12 $\pm$ 1.66, p < 0.001), and dual-domain feature fusion approaches (4.05 $\pm$ 0.88, p < 0.001).
<!-- entry:000130:end -->
<!-- entry:000131:start -->
## [000131] paper — 2026-09-17T13:59:06
arXiv ID: 1908.06006
Title: Bidirectional Context-Aware Hierarchical Attention Network for Document Understanding
Authors: Jean-Baptiste Remy, Antoine Jean-Pierre Tixier, Michalis Vazirgiannis
Categories: cs.CL, cs.LG
Published: 2019-08-16T15:20:04+00:00
Local file: papers/raw/1908.06006.md (full text retrieved)
Abstract: The Hierarchical Attention Network (HAN) has made great strides, but it suffers a major limitation: at level 1, each sentence is encoded in complete isolation. In this work, we propose and compare several modifications of HAN in which the sentence encoder is able to make context-aware attentional decisions (CAHAN). Furthermore, we propose a bidirectional document encoder that processes the document forwards and backwards, using the preceding and following sentences as context. Experiments on three large-scale sentiment and topic classification datasets show that the bidirectional version of CAHAN outperforms HAN everywhere, with only a modest increase in computation time. While results are promising, we expect the superiority of CAHAN to be even more evident on tasks requiring a deeper understanding of the input documents, such as abstractive summarization. Code is publicly available.
<!-- entry:000131:end -->
<!-- entry:000132:start -->
## [000132] paper — 2026-09-17T13:59:11
arXiv ID: 2407.01424
Title: A Global-Local Attention Mechanism for Relation Classification
Authors: Yiping Sun
Categories: cs.CL, cs.IR
Published: 2024-07-01T16:14:25+00:00
Local file: papers/raw/2407.01424.md (full text retrieved)
Abstract: Relation classification, a crucial component of relation extraction, involves identifying connections between two entities. Previous studies have predominantly focused on integrating the attention mechanism into relation classification at a global scale, overlooking the importance of the local context. To address this gap, this paper introduces a novel global-local attention mechanism for relation classification, which enhances global attention with a localized focus. Additionally, we propose innovative hard and soft localization mechanisms to identify potential keywords for local attention. By incorporating both hard and soft localization strategies, our approach offers a more nuanced and comprehensive understanding of the contextual cues that contribute to effective relation classification. Our experimental results on the SemEval-2010 Task 8 dataset highlight the superior performance of our method compared to previous attention-based approaches in relation classification.
<!-- entry:000132:end -->
<!-- entry:000133:start -->
## [000133] paper — 2026-09-17T13:59:13
arXiv ID: 1810.05932
Title: Spatial-Temporal Densely Connected Convolutional Networks: An Application to CO2 Leakage Detection
Authors: Zheng Zhou, Youzuo Lin, Yue Wu, Zan Wang, Robert Dilmore, George Guthrie
Categories: physics.geo-ph
Published: 2018-10-13T21:53:32+00:00
Local file: papers/raw/1810.05932.md (full text retrieved)
Abstract: In carbon capture and sequestration, building an effective monitoring method is a crucial step to detect and respond to CO2 leakage. CO2 leakage detection methods rely on geophysical observations and monitoring sensor network. However, traditional methods usually require physical models to be interpreted by experts, and the accuracy of these methods will be restricted by different application conditions. In this paper, we develop a novel data-driven detection method based on densely connected convolutional networks. Our detection method learns a mapping relation between seismic data and the CO2 leakage mass. To account for the spatial and temporal characteristics of seismic data, we design a novel network architecture by combining 1-D and 2-D convolutional neural networks together. To overcome the expensive computational cost, we further apply a densely-connecting policy to our network architecture to reduce the network parameters. We employ our detection method to synthetic seismic datasets using Kimberlina model. The numerical results show that our leakage detection method accurately detects the leakage mass. Therefore, our novel CO2 leakage detection method has great potential for monitoring CO2 storage.
<!-- entry:000133:end -->
<!-- entry:000134:start -->
## [000134] paper — 2026-09-17T13:59:17
arXiv ID: 2505.24595
Title: BinConv: A Neural Architecture for Ordinal Encoding in Time-Series Forecasting
Authors: Andrei Chernov, Vitaliy Pozdnyakov, Ilya Makarov
Categories: cs.LG, cs.AI, stat.ML
Published: 2025-05-30T13:41:39+00:00
Local file: papers/raw/2505.24595.md (full text retrieved)
Abstract: Recent work in time series forecasting has explored reformulating regression as a classification task. By discretizing the continuous target space into bins and predicting over a fixed set of classes, these approaches benefit from more stable training, improved uncertainty modeling, and compatibility with modern deep learning architectures. However, most existing methods rely on one-hot encoding, which ignores the inherent ordinal structure of the target values. As a result, they fail to convey information about the relative distance between predicted and true values during training. In this paper, we address this limitation by applying \textbf{Cumulative Binary Encoding} (CBE), a monotonic binary representation that transforms both model inputs and outputs. CBE implicitly preserves ordinal and magnitude information, allowing models to learn distance aware representations while operating within a classification framework. To leverage CBE effectively, we propose \textbf{BinConv}, a fully convolutional neural network architecture designed for probabilistic forecasting. We demonstrate that standard fully connected layers are not only less computationally efficient than convolutional layers when used with CBE, but also degrade forecasting performance. Our experiments on standard benchmark datasets show that BinConv achieves superior performance compared to widely used baselines in both point and probabilistic forecasting, while requiring fewer parameters and enabling faster training.
<!-- entry:000134:end -->
<!-- entry:000135:start -->
## [000135] paper — 2026-09-17T13:59:26
arXiv ID: 2012.01900
Title: Light-field view synthesis using convolutional block attention module
Authors: M. Shahzeb Khan Gul, Umair Mukati, Michel Bätz, Søren Forchhammer, Joachim Keinert
Categories: eess.IV
Published: 2020-12-03T13:26:39+00:00
Local file: papers/raw/2012.01900.md (full text retrieved)
Abstract: Consumer light-field (LF) cameras suffer from a low or limited resolution because of the angular-spatial trade-off. To alleviate this drawback, we propose a novel learning-based approach utilizing attention mechanism to synthesize novel views of a light-field image using a sparse set of input views (i.e., 4 corner views) from a camera array. In the proposed method, we divide the process into three stages, stereo-feature extraction, disparity estimation, and final image refinement. We use three sequential convolutional neural networks for each stage. A residual convolutional block attention module (CBAM) is employed for final adaptive image refinement. Attention modules are helpful in learning and focusing more on the important features of the image and are thus sequentially applied in the channel and spatial dimensions. Experimental results show the robustness of the proposed method. Our proposed network outperforms the state-of-the-art learning-based light-field view synthesis methods on two challenging real-world datasets by 0.5 dB on average. Furthermore, we provide an ablation study to substantiate our findings.
<!-- entry:000135:end -->
<!-- entry:000136:start -->
## [000136] paper — 2026-09-17T13:59:34
arXiv ID: 2406.09656
Title: RSEND: Retinex-based Squeeze and Excitation Network with Dark Region Detection for Efficient Low Light Image Enhancement
Authors: Jingcheng Li, Ye Qiao, Haocheng Xu, Sitao Huang
Categories: cs.CV, cs.AI, cs.LG, eess.IV
Published: 2024-06-14T01:36:52+00:00
Local file: papers/raw/2406.09656.md (full text retrieved)
Abstract: Images captured under low-light scenarios often suffer from low quality. Previous CNN-based deep learning methods often involve using Retinex theory. Nevertheless, most of them cannot perform well in more complicated datasets like LOL-v2 while consuming too much computational resources. Besides, some of these methods require sophisticated training at different stages, making the procedure even more time-consuming and tedious. In this paper, we propose a more accurate, concise, and one-stage Retinex theory based framework, RSEND. RSEND first divides the low-light image into the illumination map and reflectance map, then captures the important details in the illumination map and performs light enhancement. After this step, it refines the enhanced gray-scale image and does element-wise matrix multiplication with the reflectance map. By denoising the output it has from the previous step, it obtains the final result. In all the steps, RSEND utilizes Squeeze and Excitation network to better capture the details. Comprehensive quantitative and qualitative experiments show that our Efficient Retinex model significantly outperforms other CNN-based models, achieving a PSNR improvement ranging from 0.44 dB to 4.2 dB in different datasets and even outperforms transformer-based models in the LOL-v2-real dataset.
<!-- entry:000136:end -->
<!-- entry:000137:start -->
## [000137] paper — 2026-09-17T13:59:37
arXiv ID: 2002.03740
Title: Convolutional Hierarchical Attention Network for Query-Focused Video Summarization
Authors: Shuwen Xiao, Zhou Zhao, Zijian Zhang, Xiaohui Yan, Min Yang
Categories: cs.CV
Published: 2020-01-31T04:30:14+00:00
Local file: papers/raw/2002.03740.md (full text retrieved)
Abstract: Previous approaches for video summarization mainly concentrate on finding the most diverse and representative visual contents as video summary without considering the user's preference. This paper addresses the task of query-focused video summarization, which takes user's query and a long video as inputs and aims to generate a query-focused video summary. In this paper, we consider the task as a problem of computing similarity between video shots and query. To this end, we propose a method, named Convolutional Hierarchical Attention Network (CHAN), which consists of two parts: feature encoding network and query-relevance computing module. In the encoding network, we employ a convolutional network with local self-attention mechanism and query-aware global attention mechanism to learns visual information of each shot. The encoded features will be sent to query-relevance computing module to generate queryfocused video summary. Extensive experiments on the benchmark dataset demonstrate the competitive performance and show the effectiveness of our approach.
<!-- entry:000137:end -->
<!-- entry:000138:start -->
## [000138] paper — 2026-09-17T13:59:44
arXiv ID: 2504.18689
Title: HierSum: A Global and Local Attention Mechanism for Video Summarization
Authors: Apoorva Beedu, Irfan Essa
Categories: cs.CV, cs.AI, cs.LG
Published: 2025-04-25T20:30:30+00:00
Local file: papers/raw/2504.18689.md (full text retrieved)
Abstract: Video summarization creates an abridged version (i.e., a summary) that provides a quick overview of the video while retaining pertinent information. In this work, we focus on summarizing instructional videos and propose a method for breaking down a video into meaningful segments, each corresponding to essential steps in the video. We propose \textbf{HierSum}, a hierarchical approach that integrates fine-grained local cues from subtitles with global contextual information provided by video-level instructions. Our approach utilizes the ``most replayed" statistic as a supervisory signal to identify critical segments, thereby improving the effectiveness of the summary. We evaluate on benchmark datasets such as TVSum, BLiSS, Mr.HiSum, and the WikiHow test set, and show that HierSum consistently outperforms existing methods in key metrics such as F1-score and rank correlation. We also curate a new multi-modal dataset using WikiHow and EHow videos and associated articles containing step-by-step instructions. Through extensive ablation studies, we demonstrate that training on this dataset significantly enhances summarization on the target datasets.
<!-- entry:000138:end -->
<!-- entry:000139:start -->
## [000139] paper — 2026-09-17T14:12:49
arXiv ID: 1707.06347
Title: Proximal Policy Optimization Algorithms
Authors: John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, Oleg Klimov
Categories: cs.LG
Published: 2017-07-20T02:32:33+00:00
Local file: papers/raw/1707.06347.md (full text retrieved)
Abstract: We propose a new family of policy gradient methods for reinforcement learning, which alternate between sampling data through interaction with the environment, and optimizing a "surrogate" objective function using stochastic gradient ascent. Whereas standard policy gradient methods perform one gradient update per data sample, we propose a novel objective function that enables multiple epochs of minibatch updates. The new methods, which we call proximal policy optimization (PPO), have some of the benefits of trust region policy optimization (TRPO), but they are much simpler to implement, more general, and have better sample complexity (empirically). Our experiments test PPO on a collection of benchmark tasks, including simulated robotic locomotion and Atari game playing, and we show that PPO outperforms other online policy gradient methods, and overall strikes a favorable balance between sample complexity, simplicity, and wall-time.
<!-- entry:000139:end -->
<!-- entry:000140:start -->
## [000140] paper — 2026-09-17T14:12:52
arXiv ID: 1706.03741
Title: Deep reinforcement learning from human preferences
Authors: Paul Christiano, Jan Leike, Tom B. Brown, Miljan Martic, Shane Legg, Dario Amodei
Categories: stat.ML, cs.AI, cs.HC, cs.LG
Published: 2017-06-12T17:23:59+00:00
Local file: papers/raw/1706.03741.md (full text retrieved)
Abstract: For sophisticated reinforcement learning (RL) systems to interact usefully with real-world environments, we need to communicate complex goals to these systems. In this work, we explore goals defined in terms of (non-expert) human preferences between pairs of trajectory segments. We show that this approach can effectively solve complex RL tasks without access to the reward function, including Atari games and simulated robot locomotion, while providing feedback on less than one percent of our agent's interactions with the environment. This reduces the cost of human oversight far enough that it can be practically applied to state-of-the-art RL systems. To demonstrate the flexibility of our approach, we show that we can successfully train complex novel behaviors with about an hour of human time. These behaviors and environments are considerably more complex than any that have been previously learned from human feedback.
<!-- entry:000140:end -->
<!-- entry:000141:start -->
## [000141] paper — 2026-09-17T14:13:13
arXiv ID: 1909.08593
Title: Fine-Tuning Language Models from Human Preferences
Authors: Daniel M. Ziegler, Nisan Stiennon, Jeffrey Wu, Tom B. Brown, Alec Radford, Dario Amodei, Paul Christiano, Geoffrey Irving
Categories: cs.CL, cs.LG, stat.ML
Published: 2019-09-18T17:33:39+00:00
Local file: papers/raw/1909.08593.md (full text retrieved)
Abstract: Reward learning enables the application of reinforcement learning (RL) to tasks where reward is defined by human judgment, building a model of reward by asking humans questions. Most work on reward learning has used simulated environments, but complex information about values is often expressed in natural language, and we believe reward learning for language is a key to making RL practical and safe for real-world tasks. In this paper, we build on advances in generative pretraining of language models to apply reward learning to four natural language tasks: continuing text with positive sentiment or physically descriptive language, and summarization tasks on the TL;DR and CNN/Daily Mail datasets. For stylistic continuation we achieve good results with only 5,000 comparisons evaluated by humans. For summarization, models trained with 60,000 comparisons copy whole sentences from the input but skip irrelevant preamble; this leads to reasonable ROUGE scores and very good performance according to our human labelers, but may be exploiting the fact that labelers rely on simple heuristics.
<!-- entry:000141:end -->
<!-- entry:000142:start -->
## [000142] paper — 2026-09-17T14:13:16
arXiv ID: 2203.02155
Title: Training language models to follow instructions with human feedback
Authors: Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Carroll L. Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, John Schulman, Jacob Hilton, Fraser Kelton, Luke Miller, Maddie Simens, Amanda Askell, Peter Welinder, Paul Christiano, Jan Leike, Ryan Lowe
Categories: cs.CL, cs.AI, cs.LG
Published: 2022-03-04T07:04:42+00:00
Local file: papers/raw/2203.02155.md (full text retrieved)
Abstract: Making language models bigger does not inherently make them better at following a user's intent. For example, large language models can generate outputs that are untruthful, toxic, or simply not helpful to the user. In other words, these models are not aligned with their users. In this paper, we show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback. Starting with a set of labeler-written prompts and prompts submitted through the OpenAI API, we collect a dataset of labeler demonstrations of the desired model behavior, which we use to fine-tune GPT-3 using supervised learning. We then collect a dataset of rankings of model outputs, which we use to further fine-tune this supervised model using reinforcement learning from human feedback. We call the resulting models InstructGPT. In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. Moreover, InstructGPT models show improvements in truthfulness and reductions in toxic output generation while having minimal performance regressions on public NLP datasets. Even though InstructGPT still makes simple mistakes, our results show that fine-tuning with human feedback is a promising direction for aligning language models with human intent.
<!-- entry:000142:end -->
<!-- entry:000143:start -->
## [000143] paper — 2026-09-17T14:13:22
arXiv ID: 2204.05862
Title: Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback
Authors: Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, Nicholas Joseph, Saurav Kadavath, Jackson Kernion, Tom Conerly, Sheer El-Showk, Nelson Elhage, Zac Hatfield-Dodds, Danny Hernandez, Tristan Hume, Scott Johnston, Shauna Kravec, Liane Lovitt, Neel Nanda, Catherine Olsson, Dario Amodei, Tom Brown, Jack Clark, Sam McCandlish, Chris Olah, Ben Mann, Jared Kaplan
Categories: cs.CL, cs.LG
Published: 2022-04-12T15:02:38+00:00
Local file: papers/raw/2204.05862.md (full text retrieved)
Abstract: We apply preference modeling and reinforcement learning from human feedback (RLHF) to finetune language models to act as helpful and harmless assistants. We find this alignment training improves performance on almost all NLP evaluations, and is fully compatible with training for specialized skills such as python coding and summarization. We explore an iterated online mode of training, where preference models and RL policies are updated on a weekly cadence with fresh human feedback data, efficiently improving our datasets and models. Finally, we investigate the robustness of RLHF training, and identify a roughly linear relation between the RL reward and the square root of the KL divergence between the policy and its initialization. Alongside our main results, we perform peripheral analyses on calibration, competing objectives, and the use of OOD detection, compare our models with human writers, and provide samples from our models using prompts appearing in recent related work.
<!-- entry:000143:end -->
<!-- entry:000144:start -->
## [000144] paper — 2026-09-17T14:13:24
arXiv ID: 2212.08073
Title: Constitutional AI: Harmlessness from AI Feedback
Authors: Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson, Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli, Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage, Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby, Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec, Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume, Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei, Nicholas Joseph, Sam McCandlish, Tom Brown, Jared Kaplan
Categories: cs.CL, cs.AI
Published: 2022-12-15T06:19:23+00:00
Local file: papers/raw/2212.08073.md (full text retrieved)
Abstract: As AI systems become more capable, we would like to enlist their help to supervise other AIs. We experiment with methods for training a harmless AI assistant through self-improvement, without any human labels identifying harmful outputs. The only human oversight is provided through a list of rules or principles, and so we refer to the method as 'Constitutional AI'. The process involves both a supervised learning and a reinforcement learning phase. In the supervised phase we sample from an initial model, then generate self-critiques and revisions, and then finetune the original model on revised responses. In the RL phase, we sample from the finetuned model, use a model to evaluate which of the two samples is better, and then train a preference model from this dataset of AI preferences. We then train with RL using the preference model as the reward signal, i.e. we use 'RL from AI Feedback' (RLAIF). As a result we are able to train a harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections to them. Both the SL and RL methods can leverage chain-of-thought style reasoning to improve the human-judged performance and transparency of AI decision making. These methods make it possible to control AI behavior more precisely and with far fewer human labels.
<!-- entry:000144:end -->
<!-- entry:000145:start -->
## [000145] paper — 2026-09-17T14:13:27
arXiv ID: 2305.18290
Title: Direct Preference Optimization: Your Language Model is Secretly a Reward Model
Authors: Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D. Manning, Chelsea Finn
Categories: cs.LG, cs.AI, cs.CL
Published: 2023-05-29T17:57:46+00:00
Local file: papers/raw/2305.18290.md (full text retrieved)
Abstract: While large-scale unsupervised language models (LMs) learn broad world knowledge and some reasoning skills, achieving precise control of their behavior is difficult due to the completely unsupervised nature of their training. Existing methods for gaining such steerability collect human labels of the relative quality of model generations and fine-tune the unsupervised LM to align with these preferences, often with reinforcement learning from human feedback (RLHF). However, RLHF is a complex and often unstable procedure, first fitting a reward model that reflects the human preferences, and then fine-tuning the large unsupervised LM using reinforcement learning to maximize this estimated reward without drifting too far from the original model. In this paper we introduce a new parameterization of the reward model in RLHF that enables extraction of the corresponding optimal policy in closed form, allowing us to solve the standard RLHF problem with only a simple classification loss. The resulting algorithm, which we call Direct Preference Optimization (DPO), is stable, performant, and computationally lightweight, eliminating the need for sampling from the LM during fine-tuning or performing significant hyperparameter tuning. Our experiments show that DPO can fine-tune LMs to align with human preferences as well as or better than existing methods. Notably, fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations, and matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train.
<!-- entry:000145:end -->
<!-- entry:000146:start -->
## [000146] paper — 2026-09-17T14:14:43
arXiv ID: 2407.17482
Title: Reinforcement Learning from Human Feedback: Whose Culture, Whose Values, Whose Perspectives?
Authors: Kristian González Barman, Simon Lohse, Henk de Regt
Categories: cs.CY, cs.AI, cs.CL, cs.HC
Published: 2024-07-02T08:07:27+00:00
Local file: papers/raw/2407.17482.md (full text retrieved)
Abstract: We argue for the epistemic and ethical advantages of pluralism in Reinforcement Learning from Human Feedback (RLHF) in the context of Large Language Models (LLM). Drawing on social epistemology and pluralist philosophy of science, we suggest ways in which RHLF can be made more responsive to human needs and how we can address challenges along the way. The paper concludes with an agenda for change, i.e. concrete, actionable steps to improve LLM development.
<!-- entry:000146:end -->
<!-- entry:000147:start -->
## [000147] paper — 2026-09-17T14:14:47
arXiv ID: 2405.17956
Title: Unified Preference Optimization: Language Model Alignment Beyond the Preference Frontier
Authors: Anirudhan Badrinath, Prabhat Agarwal, Jiajing Xu
Categories: cs.AI
Published: 2024-05-28T08:35:48+00:00
Local file: papers/raw/2405.17956.md (full text retrieved)
Abstract: For aligning large language models (LLMs), prior work has leveraged reinforcement learning via human feedback (RLHF) or variations of direct preference optimization (DPO). While DPO offers a simpler framework based on maximum likelihood estimation, it compromises on the ability to easily tune language models to maximize auxiliary, non-preferential objectives according to the LLM designer's preferences (e.g., tuning lexical style or minimizing specific kinds of harmful content). Critically, these designer objectives may not be amply human-labeled or represented in available data, align with user preferences, or even be able to be captured tractably by binary preference pairs. To leverage the simplicity and performance of DPO with the generality of RL, we propose a unified approach. Based on a simple decomposition of preference and auxiliary objectives, we allow for tuning LLMs to optimize user and designer preferences without any additional specialized or preference data, computational cost, stability ``tweaks'', or training instability. The proposed method, Unified Preference Optimization, shows the ability to effectively generalize to user preferences and auxiliary objectives, while preserving or surpassing alignment performance on challenging benchmarks across a range of model sizes.
<!-- entry:000147:end -->
<!-- entry:000148:start -->
## [000148] paper — 2026-09-17T14:14:49
arXiv ID: 2604.06621
Title: The Theorems of Dr. David Blackwell and Their Contributions to Artificial Intelligence
Authors: Napoleon Paxton
Categories: cs.GL, cs.LG, stat.ML
Published: 2026-04-08T03:01:58+00:00
Local file: papers/raw/2604.06621.md (full text retrieved)
Abstract: Dr. David Blackwell was a mathematician and statistician of the first rank, whose contributions to statistical theory, game theory, and decision theory predated many of the algorithmic breakthroughs that define modern artificial intelligence. This survey examines three of his most consequential theoretical results the Rao Blackwell theorem, the Blackwell Approachability theorem, and the Blackwell Informativeness theorem (comparison of experiments) and traces their direct influence on contemporary AI and machine learning. We show that these results, developed primarily in the 1940s and 1950s, remain technically live across modern subfields including Markov Chain Monte Carlo inference, autonomous mobile robot navigation (SLAM), generative model training, no-regret online learning, reinforcement learning from human feedback (RLHF), large language model alignment, and information design. NVIDIAs 2024 decision to name their flagship GPU architecture (Blackwell) provides vivid testament to his enduring relevance. We also document an emerging frontier: explicit Rao Blackwellized variance reduction in LLM RLHF pipelines, recently proposed but not yet standard practice. Together, Blackwell theorems form a unified framework addressing information compression, sequential decision making under uncertainty, and the comparison of information sources precisely the problems at the core of modern AI.
<!-- entry:000148:end -->
<!-- entry:000149:start -->
## [000149] paper — 2026-09-17T14:14:55
arXiv ID: 1807.10299
Title: Variational Option Discovery Algorithms
Authors: Joshua Achiam, Harrison Edwards, Dario Amodei, Pieter Abbeel
Categories: cs.AI
Published: 2018-07-26T18:05:45+00:00
Local file: papers/raw/1807.10299.md (full text retrieved)
Abstract: We explore methods for option discovery based on variational inference and make two algorithmic contributions. First: we highlight a tight connection between variational option discovery methods and variational autoencoders, and introduce Variational Autoencoding Learning of Options by Reinforcement (VALOR), a new method derived from the connection. In VALOR, the policy encodes contexts from a noise distribution into trajectories, and the decoder recovers the contexts from the complete trajectories. Second: we propose a curriculum learning approach where the number of contexts seen by the agent increases whenever the agent's performance is strong enough (as measured by the decoder) on the current set of contexts. We show that this simple trick stabilizes training for VALOR and prior variational option discovery methods, allowing a single agent to learn many more modes of behavior than it could with a fixed context distribution. Finally, we investigate other topics related to variational option discovery, including fundamental limitations of the general approach and the applicability of learned options to downstream tasks.
<!-- entry:000149:end -->
<!-- entry:000150:start -->
## [000150] paper — 2026-09-17T14:14:59
arXiv ID: 2009.01325
Title: Learning to summarize from human feedback
Authors: Nisan Stiennon, Long Ouyang, Jeff Wu, Daniel M. Ziegler, Ryan Lowe, Chelsea Voss, Alec Radford, Dario Amodei, Paul Christiano
Categories: cs.CL, cs.AI, cs.LG
Published: 2020-09-02T19:54:41+00:00
Local file: papers/raw/2009.01325.md (full text retrieved)
Abstract: As language models become more powerful, training and evaluation are increasingly bottlenecked by the data and metrics used for a particular task. For example, summarization models are often trained to predict human reference summaries and evaluated using ROUGE, but both of these metrics are rough proxies for what we really care about -- summary quality. In this work, we show that it is possible to significantly improve summary quality by training a model to optimize for human preferences. We collect a large, high-quality dataset of human comparisons between summaries, train a model to predict the human-preferred summary, and use that model as a reward function to fine-tune a summarization policy using reinforcement learning. We apply our method to a version of the TL;DR dataset of Reddit posts and find that our models significantly outperform both human reference summaries and much larger models fine-tuned with supervised learning alone. Our models also transfer to CNN/DM news articles, producing summaries nearly as good as the human reference without any news-specific fine-tuning. We conduct extensive analyses to understand our human feedback dataset and fine-tuned models We establish that our reward model generalizes to new datasets, and that optimizing our reward model results in better summaries than optimizing ROUGE according to humans. We hope the evidence from our paper motivates machine learning researchers to pay closer attention to how their training loss affects the model behavior they actually want.
<!-- entry:000150:end -->
<!-- entry:000151:start -->
## [000151] paper — 2026-09-17T14:15:04
arXiv ID: 2005.14165
Title: Language Models are Few-Shot Learners
Authors: Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, Dario Amodei
Categories: cs.CL
Published: 2020-05-28T17:29:03+00:00
Local file: papers/raw/2005.14165.md (full text retrieved)
Abstract: Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples. By contrast, humans can generally perform a new language task from only a few examples or from simple instructions - something which current NLP systems still largely struggle to do. Here we show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches. Specifically, we train GPT-3, an autoregressive language model with 175 billion parameters, 10x more than any previous non-sparse language model, and test its performance in the few-shot setting. For all tasks, GPT-3 is applied without any gradient updates or fine-tuning, with tasks and few-shot demonstrations specified purely via text interaction with the model. GPT-3 achieves strong performance on many NLP datasets, including translation, question-answering, and cloze tasks, as well as several tasks that require on-the-fly reasoning or domain adaptation, such as unscrambling words, using a novel word in a sentence, or performing 3-digit arithmetic. At the same time, we also identify some datasets where GPT-3's few-shot learning still struggles, as well as some datasets where GPT-3 faces methodological issues related to training on large web corpora. Finally, we find that GPT-3 can generate samples of news articles which human evaluators have difficulty distinguishing from articles written by humans. We discuss broader societal impacts of this finding and of GPT-3 in general.
<!-- entry:000151:end -->
<!-- entry:000152:start -->
## [000152] paper — 2026-09-17T14:15:23
arXiv ID: 1710.09767
Title: Meta Learning Shared Hierarchies
Authors: Kevin Frans, Jonathan Ho, Xi Chen, Pieter Abbeel, John Schulman
Categories: cs.LG
Published: 2017-10-26T15:43:33+00:00
Local file: papers/raw/1710.09767.md (full text retrieved)
Abstract: We develop a metalearning approach for learning hierarchically structured policies, improving sample efficiency on unseen tasks through the use of shared primitives---policies that are executed for large numbers of timesteps. Specifically, a set of primitives are shared within a distribution of tasks, and are switched between by task-specific policies. We provide a concrete metric for measuring the strength of such hierarchies, leading to an optimization problem for quickly reaching high reward on unseen tasks. We then present an algorithm to solve this problem end-to-end through the use of any off-the-shelf reinforcement learning method, by repeatedly sampling new tasks and resetting task-specific policies. We successfully discover meaningful motor primitives for the directional movement of four-legged robots, solely by interacting with distributions of mazes. We also demonstrate the transferability of primitives to solve long-timescale sparse-reward obstacle courses, and we enable 3D humanoid robots to robustly walk and crawl with the same policy.
<!-- entry:000152:end -->
<!-- entry:000153:start -->
## [000153] paper — 2026-09-17T14:15:26
arXiv ID: 1704.01444
Title: Learning to Generate Reviews and Discovering Sentiment
Authors: Alec Radford, Rafal Jozefowicz, Ilya Sutskever
Categories: cs.LG, cs.CL, cs.NE
Published: 2017-04-05T14:20:28+00:00
Local file: papers/raw/1704.01444.md (full text retrieved)
Abstract: We explore the properties of byte-level recurrent language models. When given sufficient amounts of capacity, training data, and compute time, the representations learned by these models include disentangled features corresponding to high-level concepts. Specifically, we find a single unit which performs sentiment analysis. These representations, learned in an unsupervised manner, achieve state of the art on the binary subset of the Stanford Sentiment Treebank. They are also very data efficient. When using only a handful of labeled examples, our approach matches the performance of strong baselines trained on full datasets. We also demonstrate the sentiment unit has a direct influence on the generative process of the model. Simply fixing its value to be positive or negative generates samples with the corresponding positive or negative sentiment.
<!-- entry:000153:end -->
<!-- entry:000154:start -->
## [000154] paper — 2026-09-17T14:15:29
arXiv ID: 1401.5351
Title: Ranking Function Synthesis for Linear Lasso Programs
Authors: Jan Leike
Categories: cs.LO
Published: 2014-01-21T15:36:43+00:00
Local file: papers/raw/1401.5351.md (full text retrieved)
Abstract: The scope of this work is the constraint-based synthesis of termination arguments for the restricted class of programs called linear lasso programs. A termination argument consists of a ranking function as well as a set of supporting invariants.   We extend existing methods in several ways. First, we use Motzkin's Transposition Theorem instead of Farkas' Lemma. This allows us to consider linear lasso programs that can additionally contain strict inequalities. Existing methods are restricted to non-strict inequalities and equalities.   Second, we consider several kinds of ranking functions: affine-linear, piecewise and lexicographic ranking functions. Moreover, we present a novel kind of ranking function called multiphase ranking function which proceeds through a fixed number of phases such that for each phase, there is an affine-linear ranking function. As an abstraction to the synthesis of specific ranking functions, we introduce the notion ranking function template. This enables us to handle all ranking functions in a unified way.   Our method relies on non-linear algebraic constraint solving as a subroutine which is known to scale poorly to large problems. As a mitigation we formalize an assessment of the difficulty of our constraints and present an argument why they are of an easier kind than general non-linear constraints.   We prove our method to be complete: if there is a termination argument of the form specified by the given ranking function template with a fixed number of affine-linear supporting invariants, then our method will find a termination argument.   To our knowledge, the approach we propose is the most powerful technique of synthesis-based discovery of termination arguments for linear lasso programs and encompasses and enhances several methods having been proposed thus far.
<!-- entry:000154:end -->
<!-- entry:000155:start -->
## [000155] paper — 2026-09-17T14:15:39
arXiv ID: 2005.04305
Title: Measuring the Algorithmic Efficiency of Neural Networks
Authors: Danny Hernandez, Tom B. Brown
Categories: cs.LG, cs.CV, stat.ML
Published: 2020-05-08T22:26:37+00:00
Local file: papers/raw/2005.04305.md (full text retrieved)
Abstract: Three factors drive the advance of AI: algorithmic innovation, data, and the amount of compute available for training. Algorithmic progress has traditionally been more difficult to quantify than compute and data. In this work, we argue that algorithmic progress has an aspect that is both straightforward to measure and interesting: reductions over time in the compute needed to reach past capabilities. We show that the number of floating-point operations required to train a classifier to AlexNet-level performance on ImageNet has decreased by a factor of 44x between 2012 and 2019. This corresponds to algorithmic efficiency doubling every 16 months over a period of 7 years. By contrast, Moore's Law would only have yielded an 11x cost improvement. We observe that hardware and algorithmic efficiency gains multiply and can be on a similar scale over meaningful horizons, which suggests that a good model of AI progress should integrate measures from both.
<!-- entry:000155:end -->
<!-- entry:000156:start -->
## [000156] paper — 2026-09-17T14:15:45
arXiv ID: 2012.03608
Title: Gravitational-wave physics with Cosmic Explorer: limits to low-frequency sensitivity
Authors: Evan D. Hall, Kevin Kuns, Joshua R. Smith, Yuntao Bai, Christopher Wipf, Sebastien Biscans, Rana X Adhikari, Koji Arai, Stefan Ballmer, Lisa Barsotti, Yanbei Chen, Matthew Evans, Peter Fritschel, Jan Harms, Brittany Kamai, Jameson Graef Rollins, David Shoemaker, Bram Slagmolen, Rainer Weiss, Hiro Yamamoto
Categories: gr-qc, astro-ph.IM
Published: 2020-12-07T11:49:21+00:00
Local file: papers/raw/2012.03608.md (full text retrieved)
Abstract: Cosmic Explorer (CE) is a next-generation ground-based gravitational-wave observatory concept, envisioned to begin operation in the 2030s, and expected to be capable of observing binary neutron star and black hole mergers back to the time of the first stars. Cosmic Explorer's sensitive band will extend below 10 Hz, where the design is predominantly limited by geophysical, thermal, and quantum noises. In this work, thermal, seismic, gravity-gradient, quantum, residual gas, scattered-light, and servo-control noises are analyzed in order to motivate facility and vacuum system design requirements, potential test mass suspensions, Newtonian noise reduction strategies, improved inertial sensors, and cryogenic control requirements. Our analysis shows that with improved technologies, Cosmic Explorer can deliver a strain sensitivity better than $10^{-23}/\mathrm{Hz}^{1/2}$ down to 5 Hz. Our work refines and extends previous analysis of the Cosmic Explorer concept and outlines the key research areas needed to make this observatory a reality.
<!-- entry:000156:end -->
<!-- entry:000157:start -->
## [000157] paper — 2026-09-17T14:15:49
arXiv ID: 2403.10704
Title: Parameter Efficient Reinforcement Learning from Human Feedback
Authors: Hakim Sidahmed, Samrat Phatale, Alex Hutcheson, Zhuonan Lin, Zhang Chen, Zac Yu, Jarvis Jin, Simral Chaudhary, Roman Komarytsia, Christiane Ahlheim, Yonghao Zhu, Bowen Li, Saravanan Ganesh, Bill Byrne, Jessica Hoffmann, Hassan Mansoor, Wei Li, Abhinav Rastogi, Lucas Dixon
Categories: cs.LG, cs.AI, cs.CL
Published: 2024-03-15T21:43:46+00:00
Local file: papers/raw/2403.10704.md (full text retrieved)
Abstract: While Reinforcement Learning from Human Feedback (RLHF) effectively aligns pretrained Large Language and Vision-Language Models (LLMs, and VLMs) with human preferences, its computational cost and complexity hamper its wider adoption. To alleviate some of the computational burden of fine-tuning, parameter efficient methods, like LoRA were introduced. In this work, we empirically evaluate the setup of Parameter Efficient Reinforcement Learning from Human Feedback (PE-RLHF) that leverages LoRA fine-tuning for Reward Modeling, and Reinforcement Learning. We benchmark the PE-RLHF setup on six diverse datasets spanning summarization, harmless/helpful response generation, UI automation, and visual question answering in terms of effectiveness of the trained models, and the training resources required. Our findings show, for the first time, that PE-RLHF achieves comparable performance to RLHF, while significantly reducing training time (up to 90% faster for reward models, and 30% faster for RL), and memory footprint (up to 50% reduction for reward models, and 27% for RL). We provide comprehensive ablations across LoRA ranks, and model sizes for both reward modeling and reinforcement learning. By mitigating the computational burden associated with RLHF, we push for a broader adoption of PE-RLHF as an alignment technique for LLMs and VLMs.
<!-- entry:000157:end -->
<!-- entry:000158:start -->
## [000158] paper — 2026-09-17T14:16:18
arXiv ID: 2209.10652
Title: Toy Models of Superposition
Authors: Nelson Elhage, Tristan Hume, Catherine Olsson, Nicholas Schiefer, Tom Henighan, Shauna Kravec, Zac Hatfield-Dodds, Robert Lasenby, Dawn Drain, Carol Chen, Roger Grosse, Sam McCandlish, Jared Kaplan, Dario Amodei, Martin Wattenberg, Christopher Olah
Categories: cs.LG
Published: 2022-09-21T20:49:26+00:00
Local file: papers/raw/2209.10652.md (full text retrieved)
Abstract: Neural networks often pack many unrelated concepts into a single neuron - a puzzling phenomenon known as 'polysemanticity' which makes interpretability much more challenging. This paper provides a toy model where polysemanticity can be fully understood, arising as a result of models storing additional sparse features in "superposition." We demonstrate the existence of a phase change, a surprising connection to the geometry of uniform polytopes, and evidence of a link to adversarial examples. We also discuss potential implications for mechanistic interpretability.
<!-- entry:000158:end -->
<!-- entry:000159:start -->
## [000159] paper — 2026-09-17T14:16:21
arXiv ID: 1403.5287
Title: Online Local Learning via Semidefinite Programming
Authors: Paul Christiano
Categories: cs.LG
Published: 2014-03-20T20:36:18+00:00
Local file: papers/raw/1403.5287.md (full text retrieved)
Abstract: In many online learning problems we are interested in predicting local information about some universe of items. For example, we may want to know whether two items are in the same cluster rather than computing an assignment of items to clusters; we may want to know which of two teams will win a game rather than computing a ranking of teams. Although finding the optimal clustering or ranking is typically intractable, it may be possible to predict the relationships between items as well as if you could solve the global optimization problem exactly.   Formally, we consider an online learning problem in which a learner repeatedly guesses a pair of labels (l(x), l(y)) and receives an adversarial payoff depending on those labels. The learner's goal is to receive a payoff nearly as good as the best fixed labeling of the items. We show that a simple algorithm based on semidefinite programming can obtain asymptotically optimal regret in the case where the number of possible labels is O(1), resolving an open problem posed by Hazan, Kale, and Shalev-Schwartz. Our main technical contribution is a novel use and analysis of the log determinant regularizer, exploiting the observation that log det(A + I) upper bounds the entropy of any distribution with covariance matrix A.
<!-- entry:000159:end -->
<!-- entry:000160:start -->
## [000160] paper — 2026-09-17T14:16:24
arXiv ID: 1907.04534
Title: The Role of Cooperation in Responsible AI Development
Authors: Amanda Askell, Miles Brundage, Gillian Hadfield
Categories: cs.CY, cs.AI
Published: 2019-07-10T06:51:04+00:00
Local file: papers/raw/1907.04534.md (full text retrieved)
Abstract: In this paper, we argue that competitive pressures could incentivize AI companies to underinvest in ensuring their systems are safe, secure, and have a positive social impact. Ensuring that AI systems are developed responsibly may therefore require preventing and solving collective action problems between companies. We note that there are several key factors that improve the prospects for cooperation in collective action problems. We use this to identify strategies to improve the prospects for industry cooperation on the responsible development of AI.
<!-- entry:000160:end -->
<!-- entry:000161:start -->
## [000161] paper — 2026-09-17T14:16:27
arXiv ID: 1502.05477
Title: Trust Region Policy Optimization
Authors: John Schulman, Sergey Levine, Philipp Moritz, Michael I. Jordan, Pieter Abbeel
Categories: cs.LG
Published: 2015-02-19T06:44:25+00:00
Local file: papers/raw/1502.05477.md (full text retrieved)
Abstract: We describe an iterative procedure for optimizing policies, with guaranteed monotonic improvement. By making several approximations to the theoretically-justified procedure, we develop a practical algorithm, called Trust Region Policy Optimization (TRPO). This algorithm is similar to natural policy gradient methods and is effective for optimizing large nonlinear policies such as neural networks. Our experiments demonstrate its robust performance on a wide variety of tasks: learning simulated robotic swimming, hopping, and walking gaits; and playing Atari games using images of the screen as input. Despite its approximations that deviate from the theory, TRPO tends to give monotonic improvement, with little tuning of hyperparameters.
<!-- entry:000161:end -->
<!-- entry:000162:start -->
## [000162] paper — 2026-09-17T14:16:35
arXiv ID: 1511.06434
Title: Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks
Authors: Alec Radford, Luke Metz, Soumith Chintala
Categories: cs.LG, cs.CV
Published: 2015-11-19T22:50:32+00:00
Local file: papers/raw/1511.06434.md (full text retrieved)
Abstract: In recent years, supervised learning with convolutional networks (CNNs) has seen huge adoption in computer vision applications. Comparatively, unsupervised learning with CNNs has received less attention. In this work we hope to help bridge the gap between the success of CNNs for supervised learning and unsupervised learning. We introduce a class of CNNs called deep convolutional generative adversarial networks (DCGANs), that have certain architectural constraints, and demonstrate that they are a strong candidate for unsupervised learning. Training on various image datasets, we show convincing evidence that our deep convolutional adversarial pair learns a hierarchy of representations from object parts to scenes in both the generator and discriminator. Additionally, we use the learned features for novel tasks - demonstrating their applicability as general image representations.
<!-- entry:000162:end -->
<!-- entry:000163:start -->
## [000163] paper — 2026-09-17T14:16:38
arXiv ID: 1405.4413
Title: Geometric Series as Nontermination Arguments for Linear Lasso Programs
Authors: Jan Leike, Matthias Heizmann
Categories: cs.LO
Published: 2014-05-17T15:42:32+00:00
Local file: papers/raw/1405.4413.md (full text retrieved)
Abstract: We present a new kind of nontermination argument for linear lasso programs, called geometric nontermination argument. A geometric nontermination argument is a finite representation of an infinite execution of the form $(\vec{x} + \sum_{i=0}^t λ^i \vec{y})_{t \geq 0}$. The existence of this nontermination argument can be stated as a set of nonlinear algebraic constraints. We show that every linear loop program that has a bounded infinite execution also has a geometric nontermination argument. Furthermore, we discuss nonterminating programs that do not have a geometric nontermination argument.
<!-- entry:000163:end -->
<!-- entry:000164:start -->
## [000164] paper — 2026-09-17T14:16:41
arXiv ID: 1909.02264
Title: A phase-sensitive optomechanical amplifier for quantum noise reduction in laser interferometers
Authors: Yuntao Bai, Gautam Venugopalan, Kevin Kuns, Christopher Wipf, Aaron Markowitz, Andrew R Wade, Yanbei Chen, Rana X Adhikari
Categories: quant-ph, physics.ins-det
Published: 2019-09-05T08:46:36+00:00
Local file: papers/raw/1909.02264.md (full text retrieved)
Abstract: The sensitivity of future gravitational wave interferometers is expected to be limited through-out the detection band by quantum vacuum fluctuations, which can be reduced by quantum non-demolition methods such as squeezed vacuum injection. However, optical losses in the readout chainseverely limit the effectiveness of such schemes. We propose an optomechanical device to be installedat the output of the detector that mitigates the effect of readout loss, thus allowing the detector tobetter exploit quantum noise evasion schemes.
<!-- entry:000164:end -->
<!-- entry:000165:start -->
## [000165] paper — 2026-09-17T14:16:52
arXiv ID: 2507.04340
Title: Interactive Groupwise Comparison for Reinforcement Learning from Human Feedback
Authors: Jan Kompatscher, Danqing Shi, Giovanna Varni, Tino Weinkauf, Antti Oulasvirta
Categories: cs.LG, cs.HC
Published: 2025-07-06T10:52:14+00:00
Local file: papers/raw/2507.04340.md (full text retrieved)
Abstract: Reinforcement learning from human feedback (RLHF) has emerged as a key enabling technology for aligning AI behaviour with human preferences. The traditional way to collect data in RLHF is via pairwise comparisons: human raters are asked to indicate which one of two samples they prefer. We present an interactive visualisation that better exploits the human visual ability to compare and explore whole groups of samples. The interface is comprised of two linked views: 1) an exploration view showing a contextual overview of all sampled behaviours organised in a hierarchical clustering structure; and 2) a comparison view displaying two selected groups of behaviours for user queries. Users can efficiently explore large sets of behaviours by iterating between these two views. Additionally, we devised an active learning approach suggesting groups for comparison. As shown by our evaluation in six simulated robotics tasks, our approach increases the final rewards by 69.34%. It leads to lower error rates and better policies. We open-source the code that can be easily integrated into the RLHF training loop, supporting research on human-AI alignment.
<!-- entry:000165:end -->
<!-- entry:000166:start -->
## [000166] paper — 2026-09-17T14:16:57
arXiv ID: 2209.07858
Title: Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned
Authors: Deep Ganguli, Liane Lovitt, Jackson Kernion, Amanda Askell, Yuntao Bai, Saurav Kadavath, Ben Mann, Ethan Perez, Nicholas Schiefer, Kamal Ndousse, Andy Jones, Sam Bowman, Anna Chen, Tom Conerly, Nova DasSarma, Dawn Drain, Nelson Elhage, Sheer El-Showk, Stanislav Fort, Zac Hatfield-Dodds, Tom Henighan, Danny Hernandez, Tristan Hume, Josh Jacobson, Scott Johnston, Shauna Kravec, Catherine Olsson, Sam Ringer, Eli Tran-Johnson, Dario Amodei, Tom Brown, Nicholas Joseph, Sam McCandlish, Chris Olah, Jared Kaplan, Jack Clark
Categories: cs.CL, cs.AI, cs.CY
Published: 2022-08-23T23:37:14+00:00
Local file: papers/raw/2209.07858.md (full text retrieved)
Abstract: We describe our early efforts to red team language models in order to simultaneously discover, measure, and attempt to reduce their potentially harmful outputs. We make three main contributions. First, we investigate scaling behaviors for red teaming across 3 model sizes (2.7B, 13B, and 52B parameters) and 4 model types: a plain language model (LM); an LM prompted to be helpful, honest, and harmless; an LM with rejection sampling; and a model trained to be helpful and harmless using reinforcement learning from human feedback (RLHF). We find that the RLHF models are increasingly difficult to red team as they scale, and we find a flat trend with scale for the other model types. Second, we release our dataset of 38,961 red team attacks for others to analyze and learn from. We provide our own analysis of the data and find a variety of harmful outputs, which range from offensive language to more subtly harmful non-violent unethical outputs. Third, we exhaustively describe our instructions, processes, statistical methodologies, and uncertainty about red teaming. We hope that this transparency accelerates our ability to work together as a community in order to develop shared norms, practices, and technical standards for how to red team language models.
<!-- entry:000166:end -->
<!-- entry:000167:start -->
## [000167] paper — 2026-09-17T14:16:59
arXiv ID: 1603.06265
Title: Collaborative prediction with expert advice
Authors: Paul Christiano
Categories: cs.LG
Published: 2016-03-20T20:34:32+00:00
Local file: papers/raw/1603.06265.md (full text retrieved)
Abstract: Many practical learning systems aggregate data across many users, while learning theory traditionally considers a single learner who trusts all of their observations. A case in point is the foundational learning problem of prediction with expert advice. To date, there has been no theoretical study of the general collaborative version of prediction with expert advice, in which many users face a similar problem and would like to share their experiences in order to learn faster. A key issue in this collaborative framework is robustness: generally algorithms that aggregate data are vulnerable to manipulation by even a small number of dishonest users.   We exhibit the first robust collaborative algorithm for prediction with expert advice. When all users are honest and have similar tastes our algorithm matches the performance of pooling data and using a traditional algorithm. But our algorithm also guarantees that adding users never significantly degrades performance, even if the additional users behave adversarially. We achieve strong guarantees even when the overwhelming majority of users behave adversarially. As a special case, our algorithm is extremely robust to variation amongst the users.
<!-- entry:000167:end -->
<!-- entry:000168:start -->
## [000168] paper — 2026-09-17T14:17:20
arXiv ID: 1908.09203
Title: Release Strategies and the Social Impacts of Language Models
Authors: Irene Solaiman, Miles Brundage, Jack Clark, Amanda Askell, Ariel Herbert-Voss, Jeff Wu, Alec Radford, Gretchen Krueger, Jong Wook Kim, Sarah Kreps, Miles McCain, Alex Newhouse, Jason Blazakis, Kris McGuffie, Jasmine Wang
Categories: cs.CL, cs.AI, cs.CY
Published: 2019-08-24T20:41:40+00:00
Local file: papers/raw/1908.09203.md (full text retrieved)
Abstract: Large language models have a range of beneficial uses: they can assist in prose, poetry, and programming; analyze dataset biases; and more. However, their flexibility and generative capabilities also raise misuse concerns. This report discusses OpenAI's work related to the release of its GPT-2 language model. It discusses staged release, which allows time between model releases to conduct risk and benefit analyses as model sizes increased. It also discusses ongoing partnership-based research and provides recommendations for better coordination and responsible publication in AI.
<!-- entry:000168:end -->
<!-- entry:000169:start -->
## [000169] paper — 2026-09-17T14:17:23
arXiv ID: 1704.06440
Title: Equivalence Between Policy Gradients and Soft Q-Learning
Authors: John Schulman, Xi Chen, Pieter Abbeel
Categories: cs.LG
Published: 2017-04-21T08:33:59+00:00
Local file: papers/raw/1704.06440.md (full text retrieved)
Abstract: Two of the leading approaches for model-free reinforcement learning are policy gradient methods and $Q$-learning methods. $Q$-learning methods can be effective and sample-efficient when they work, however, it is not well-understood why they work, since empirically, the $Q$-values they estimate are very inaccurate. A partial explanation may be that $Q$-learning methods are secretly implementing policy gradient updates: we show that there is a precise equivalence between $Q$-learning and policy gradient methods in the setting of entropy-regularized reinforcement learning, that "soft" (entropy-regularized) $Q$-learning is exactly equivalent to a policy gradient method. We also point out a connection between $Q$-learning methods and natural policy gradient methods. Experimentally, we explore the entropy-regularized versions of $Q$-learning and policy gradients, and we find them to perform as well as (or slightly better than) the standard variants on the Atari benchmark. We also show that the equivalence holds in practical settings by constructing a $Q$-learning method that closely matches the learning dynamics of A3C without using a target network or $ε$-greedy exploration schedule.
<!-- entry:000169:end -->
<!-- entry:000170:start -->
## [000170] paper — 2026-09-17T14:17:26
arXiv ID: 1602.07905
Title: Thompson Sampling is Asymptotically Optimal in General Environments
Authors: Jan Leike, Tor Lattimore, Laurent Orseau, Marcus Hutter
Categories: cs.LG, cs.AI, stat.ML
Published: 2016-02-25T12:37:21+00:00
Local file: papers/raw/1602.07905.md (full text retrieved)
Abstract: We discuss a variant of Thompson sampling for nonparametric reinforcement learning in a countable classes of general stochastic environments. These environments can be non-Markov, non-ergodic, and partially observable. We show that Thompson sampling learns the environment class in the sense that (1) asymptotically its value converges to the optimal value in mean and (2) given a recoverability assumption regret is sublinear.
<!-- entry:000170:end -->
<!-- entry:000171:start -->
## [000171] paper — 2026-09-21T15:21:48
arXiv ID: 2405.13956
Local file: papers/raw/2405.13956.md (full text retrieved)
<!-- entry:000171:end -->
