# Adopción de la plantilla

Pasos que se hacen una sola vez al crear un proyecto a partir de esta plantilla. La IA borra la carpeta `setup/` en el commit de la definición inicial.

1. [x] Crea el repositorio a partir de la plantilla. Su contenido queda en `main`.
2. [x] Instala las [herramientas del README](../README.md#herramientas), con el perfil de OpenSpec, y genera las skills de OpenSpec en el repositorio. En Windows 11 puedes usar Git Bash sin WSL2: instala GNU Make desde PowerShell o Símbolo del sistema, abre una nueva terminal Git Bash y verifica que está disponible:

   ```powershell
   winget install --id ezwinports.make --exact --source winget
   ```

   ```sh
   make --version
   ```

   Si Git Bash no encuentra `make`, localiza `make.exe` en `%LOCALAPPDATA%\Microsoft\WinGet\Packages` y añade la carpeta que lo contiene a `~/.bashrc`:

   ```sh
   export PATH="<carpeta-que-contiene-make.exe>:$PATH"
   ```

   Instala OpenSpec 2.1.0, configura el perfil y sus siete etapas, y genera las skills:

   ```sh
   npm install -g @fission-ai/openspec@2.1.0
   openspec config set profile custom
   openspec config set workflows '["propose","explore","apply","update","verify","sync","archive"]'
   openspec init --tools opencode,codex --scope project
   ```

   Comprueba la CLI de GitHub y las herramientas instaladas:

   ```sh
   gh auth status
   make --version
   openspec --version
   ```

   Quedan en `.agents/skills/`, junto a las de la plantilla, y se suben con el repositorio. `openspec/config.yaml` ya pide guardarlas ahí (`skillsScope: project`).
3. [x] Ejecuta `make setup` para activar el hook de commits, crear los `.env` que falten e instalar las dependencias de los servicios:

   ```sh
   make setup
   ```
4. [x] Rellena los textos entre corchetes del [`README.md`](../README.md), incluido `[owner]/[repo]`, y borra su comentario inicial. Añade una licencia si procede.
5. [x] El repositorio ya tenía el commit inicial publicado `defd3e5` (`init`), aceptado como equivalente a `chore: adopt project template`; no se crea un commit retroactivo.
6. [x] Crea la rama `dev` desde `main` y publica las dos.
7. [x] Configura GitHub con `make github-setup`: `dev` como rama por defecto, para que `Closes #N` cierre las Issues al mergear en ella; solo *Rebase and merge* y *Create a merge commit* como métodos de merge, y las etiquetas de [`docs/ISSUE_LABELS.md`](../docs/ISSUE_LABELS.md). Necesitas permisos de administración en el repositorio.
8. [ ] Pide a la IA que empiece la fase de definición ([WORKFLOW §4](../WORKFLOW.md#4-fase-1--definición)). Se trabaja directamente en `dev`, sin rama ni PR, y al terminar la IA protege `dev` y `main` con tu aprobación (`make github-protect`).
9. [ ] Opcional: desactiva la telemetría de OpenSpec con `openspec config set telemetry.enabled false`.
