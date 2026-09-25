# Local LLM CrossFit — de AInstein al siguiente agente

Documento puente: qué es el programa, qué se hizo en AInstein (Agent #1), y el esquema del
siguiente sistema (Agent #2), un motor de juego de deducción social multiagente.

## Objetivos del "Local LLM CrossFit"

Serie de agentes, cada uno pensado como un "ejercicio" distinto, con una única regla fija:
**100% local, sin API keys de pago, sin datos saliendo de la máquina**. El objetivo no es
tener un producto pulido — es usar cada agente como excusa para tropezar de verdad con las
limitaciones de los modelos locales pequeños y aprender a diseñar alrededor de ellas, en vez
de asumir que "con un modelo más grande esto no pasaría".

Cada agente del programa debería:

- Forzar un **patrón de arquitectura distinto** al de los agentes anteriores (agente único
  con herramientas, multiagente por turnos, orquestador/trabajador, etc.), no repetir la
  misma forma con otro dominio encima.
- Probarse en serio contra un **modelo local pequeño** (la serie usa `qwen3.5:4b` como
  modelo de referencia), documentando los fallos reales encontrados y cómo se corrigieron —
  no solo el camino feliz.
- Dejar una **evaluación reproducible** (harness de pruebas, métricas, casos concretos), no
  solo "lo probé una vez y funcionó".
- Terminar en un post público (LinkedIn) contando qué se rompió y cómo se arregló — el
  aprendizaje es el producto, no solo el código.

## Agent #1 — AInstein (research agent para arXiv)

**Repo:** este mismo (`Local-research-agent`). **Estado:** funcionalmente completo, evaluado
en vivo, documentado.

**Patrón de arquitectura:** un único agente (`deepagents` sobre LangGraph) con un conjunto
grande de herramientas y un sistema de *skills* forzadas por código (middleware) en vez de
confiar en que el modelo decida solo cuándo seguir un flujo de trabajo concreto.

**Qué hace:**
- Busca, descarga y lee papers de arXiv (LaTeX → HTML → PDF como fallback), sin API key.
- Dos memorias reales: estado de conversación (checkpointer SQLite) y memoria a largo plazo
  estructurada y buscable (RAG con FAISS + reranker), además de RAG de texto completo sobre
  el contenido descargado de cada paper (chunking jerárquico padre/hijo).
- Un grafo de conocimiento (papers / autores / keywords como un único grafo heterogéneo),
  navegable por el propio agente con 4 herramientas de un salto cada una
  (`memory/graph_tools.py`) y visualizable en 3D (`memory/graph_app.py`). Se actualiza en
  vivo (nodos, aristas y similitud por keywords) cada vez que el agente toca un paper nuevo.
- Skills forzadas por código (no dejadas a criterio del modelo): `memory-management`,
  `arxiv-research`, `citation-tracking`, `paper-analysis` (3 profundidades), `knowledge-graph`,
  y dos "skills de evidencia" — `challenge-conclusion` (buscar evidencia *en contra* de una
  conclusión) y `compare-papers` (separar lo que dice el paper de la interpretación del
  agente, para saber si dos papers realmente discrepan).
- Límites de nº de llamadas a herramientas **impuestos en código**, no pedidos por prompt —
  tanto genéricos (`ToolCallLimitMiddleware`) como específicos por skill — después de que un
  bucle de llamadas real ralentizara la máquina durante las pruebas.
- Multimodal opcional y auto-detectado: OCR para PDFs escaneados, descripción de
  figuras/diagramas con un modelo de visión local si hay uno instalado.

**Aprendizajes clave (documentados en el [README](README.md#known-limitations)):**
- Un prompt de sistema grande + un resultado de herramienta grande puede disparar
  auto-resumen **a mitad de turno**, no solo entre turnos largos — y ese resumen sintético
  puede confundir a cualquier lógica que busque "el último mensaje del usuario".
- Un modelo pequeño puede citar un paper real bajo un id casi-correcto (un dígito distinto)
  y componer citas entre comillas que no están en el texto original — abierto, sin arreglar.
- El límite de contexto real necesario era más alto de lo que parecía a simple vista
  (`MIN_RECOMMENDED_NUM_CTX`), y el propio agente ahora avisa si el modelo elegido se queda
  corto.

**Contenido de la serie:** posts en `LinkedIn/` (`linkedin_post.txt` → `Linkedin_post_V2.txt`
→ `Linkedin_post_V3.txt`), más un GIF/vídeo del grafo 3D en `LinkedIn/Knowledge_graph.gif`.

## Agent #2 — motor de deducción social multiagente (siguiente)

**Objetivo de aprendizaje:** todo lo que AInstein, por ser un agente único, no obligaba a
resolver — turnos entre varios LLMs, estado privado por agente frente a estado compartido,
un orquestador de verdad (no un bucle de herramientas), y una condición de consenso/victoria
que cierra cada ronda.

### Por qué un juego de deducción social (estilo Mafia/Werewolf)

- **Roles ocultos → estado privado real.** Cada agente recibe solo su parte del contexto
  (su rol, lo que ha visto, su memoria de la partida) — nunca el estado global. Obliga a
  diseñar de cero cómo se reparte contexto entre agentes, justo lo opuesto a la memoria
  compartida de AInstein.
- **Fases con reglas distintas.** Noche (solo actúan roles especiales) y día (todos
  intervienen y votan) son transiciones de estado condicionales de verdad — el primer sitio
  donde LangGraph se usa como máquina de estados con ciclos, no como bucle de herramientas.
- **Persuasión/engaño con modelos pequeños.** ¿Puede un modelo de 4B mentir de forma
  consistente turno tras turno? ¿Los demás detectan contradicciones o solo repiten lo último
  que oyeron? Mismo tipo de pregunta que ya perseguía AInstein, en un dominio nuevo.
- **Métrica de evaluación gratis.** % de victorias por rol / por modelo / por estilo de
  persona — encaja directamente con la costumbre ya establecida de tener un harness de
  evaluación con casos reproducibles.

### Arquitectura propuesta (boceto)

`StateGraph` de LangGraph con un estado compartido (transcript público, jugadores vivos/
muertos, fase actual) y estado privado por jugador (rol, memoria propia de la partida):

- **`night_phase`** (nodo) — invoca solo a los roles especiales (p. ej. el lobo elige
  víctima); el resto de agentes ni se ejecuta en este nodo.
- **`day_phase`** (nodo) — bucle sobre jugadores vivos; cada uno recibe el transcript
  público + su memoria privada y genera una intervención (acusar, defenderse, especular).
- **`vote_phase`** (nodo) — cada jugador vivo vota; código puro (no un LLM) cuenta los votos
  y aplica la eliminación — la parte que decide el resultado nunca debe depender de que un
  modelo pequeño "sume bien".
- **Edge condicional `check_win_condition`** — código puro: ¿quedan lobos vivos? ¿quedan
  aldeanos suficientes para tener mayoría? → termina la partida o vuelve a `night_phase`.
- **Orquestador = el propio grafo**, no un LLM adicional actuando de árbitro — las reglas del
  juego son código determinista; solo el contenido de cada intervención lo genera un LLM.

**Alcance inicial:** 5–6 jugadores (1–2 lobos, resto aldeanos, quizá un vidente), para no
disparar ni el nº de llamadas por partida ni el contexto acumulado — con modelos de 4B el
transcript crece rápido y es fácil repetir el problema de truncamiento que ya apareció en
AInstein.

### Plan de evaluación

- Harness que corre N partidas completas de forma automática (mismo espíritu que
  `eval_skills.py`) y registra: ganador, nº de turnos, quién mintió y si le creyeron, en qué
  turno se destapó (si se destapó) al lobo.
- Comparar % de victorias variando: el modelo usado, el prompt/persona de cada rol, el
  nº de jugadores.
- Documentar los fallos reales encontrados (p. ej. un modelo que vota siempre al último que
  habló, o que no es capaz de mantener una mentira dos turnos seguidos) — mismo formato que
  los "Known limitations" de AInstein.

### Alternativas consideradas (descartadas por ahora, quedan como posibles Agent #3/#4)

- **Debate + juez**: 2 agentes defienden posturas opuestas, un tercero puntúa. Más simple,
  buen primer paso si el juego social resulta demasiado de golpe.
- **Negociación de recursos**: N agentes con objetivos privados (a veces contrapuestos)
  reparten algo en varias rondas — practica objetivos asimétricos sin el componente de
  engaño explícito del juego social.

## Próximos pasos inmediatos

1. Decidir repo: ¿nuevo repo separado o carpeta dentro de este mismo (`Local-research-agent`)?
2. Elegir el conjunto mínimo de roles para la primera versión jugable (recomendado: lobo +
   aldeanos, sin vidente todavía — añadir roles especiales es la iteración 2).
3. Montar el `StateGraph` con las 3 fases y la condición de victoria, probado primero con
   jugadores "tontos" (respuestas fijas/aleatorias) antes de meter LLMs de verdad — para
   validar que las reglas del juego funcionan antes de mezclar el problema del modelo con el
   problema de las reglas.
4. Conectar modelos locales reales uno a uno, empezando por una sola partida observada a
   mano (igual que las pruebas "una por una" de AInstein) antes de automatizar el harness.
