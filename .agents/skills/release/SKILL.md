---
name: release
description: Cómo preparar una versión estable, abrir el PR de promoción de dev a main y comprobar el tag y la release que crea el CI. Úsala en la fase 4 (release), también para publicar una corrección urgente.
---

# Release

Versionado en [CONTRIBUTING §9](../../../CONTRIBUTING.md#9-versiones-y-releases); el flujo, en [WORKFLOW §7](../../../WORKFLOW.md#7-fase-4--release). Trabaja sobre `dev` actualizada (`git switch dev && git pull`).

1. **Versión:** la del último tag beta sin el sufijo (`git tag --list 'v*-beta.*' --sort=-v:refname | head -n 1`). Si no hay un tag beta posterior a la última versión estable, no hay versión nueva: dilo y para.
2. **Historias incluidas:** las mergeadas en `dev` desde el último tag estable (`git log <último-estable>..origin/dev`), con su `#N`.
3. **Funcionalidades a medias:** `openspec list` muestra los cambios sin archivar y sus tareas hechas. Un cambio con parte de sus tareas hechas es una funcionalidad a medias que llegaría así a producción: nómbralo, con lo que ya está hecho.
4. ⏸ Presenta la versión, las historias y las funcionalidades a medias, y espera la aprobación.
5. **PR `dev` → `main`**, en español: título con la versión, la lista de historias con `Refs #N` (no `Closes`, ya están cerradas).
6. Espera al CI y avisa. La persona mergea con **Create a merge commit**.
7. Tras el merge, comprueba que el workflow `Tags` creó el tag `vX.Y.Z` y la GitHub Release. Si falló, informa; no crees el tag a mano.

**Corrección urgente:** cuando su `fix` ya está en `dev`, la promoción se hace enseguida con estos mismos pasos. Si hay funcionalidades a medias, la persona decide en el paso 4 entre publicarlas ya o esperar a terminarlas ([CONTRIBUTING §7](../../../CONTRIBUTING.md#correcciones-urgentes)).
