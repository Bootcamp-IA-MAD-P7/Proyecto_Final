# Adopción de la plantilla

Pasos que se hacen una sola vez al crear un proyecto a partir de esta plantilla. La IA borra la carpeta `setup/` en el commit de la definición inicial.

1. [ ] Crea el repositorio a partir de la plantilla. Su contenido queda en `main`.
2. [ ] Instala las [herramientas del README](../README.md#herramientas), con el perfil de OpenSpec, y genera las skills de OpenSpec en el repositorio:

   ```sh
   openspec init --tools opencode,codex --scope project
   ```

   Quedan en `.agents/skills/`, junto a las de la plantilla, y se suben con el repositorio. `openspec/config.yaml` ya pide guardarlas ahí (`skillsScope: project`).
3. [ ] Ejecuta `make setup` para activar el hook de commits.
4. [ ] Rellena los textos entre corchetes del [`README.md`](../README.md), incluido `[owner]/[repo]`, y borra su comentario inicial. Añade una licencia si procede.
5. [ ] Haz el commit inicial en `main`: `chore: adopt project template`.
6. [ ] Crea la rama `dev` desde `main` y publica las dos.
7. [ ] Configura GitHub con `make github-setup`: `dev` como rama por defecto, para que `Closes #N` cierre las Issues al mergear en ella; solo *Rebase and merge* y *Create a merge commit* como métodos de merge, y las etiquetas de [`docs/ISSUE_LABELS.md`](../docs/ISSUE_LABELS.md). Necesitas permisos de administración en el repositorio.
8. [ ] Pide a la IA que empiece la fase de definición ([WORKFLOW §4](../WORKFLOW.md#4-fase-1--definición)). Se trabaja directamente en `dev`, sin rama ni PR, y al terminar la IA protege `dev` y `main` con tu aprobación (`make github-protect`).
9. [ ] Opcional: desactiva la telemetría de OpenSpec con `openspec config set telemetry.enabled false`.
