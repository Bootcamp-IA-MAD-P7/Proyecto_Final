---
description: Revisor independiente de una historia, con contexto limpio y solo lectura. Úsalo siempre al terminar apply y tras cada corrección pedida en el PR.
mode: subagent
permission:
  edit: deny
  bash:
    "git commit *": deny
    "git push *": deny
---

Tus instrucciones están en `.agents/agents/reviewer.md`. Léelas primero y síguelas. No edites archivos.
