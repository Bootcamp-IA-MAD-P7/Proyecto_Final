# CoTeach-AI

CoTeach-AI es un servicio de inteligencia artificial para CoTeach que procesa grabaciones de clases de idiomas y genera transcripciones, identificación de participantes y análisis pedagógicos para profesores y alumnos. Más contexto en [`docs/PRD.md`](docs/PRD.md).

## Estado

El trabajo se sigue en [GitHub Issues](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues) y las versiones se publican en [Releases](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/releases).

## Puesta en marcha

### Herramientas

- **Docker** y **make**. En Linux y macOS, instala `make` con el gestor de paquetes de tu sistema. En Windows 11 puedes trabajar directamente con Git Bash; instala GNU Make 4.4.1 desde PowerShell o Símbolo del sistema:

  ```powershell
  winget install --id ezwinports.make --exact --source winget
  ```

  Abre una nueva terminal Git Bash y comprueba la instalación:

  ```sh
  make --version
  ```

  Si Git Bash no encuentra `make`, localiza `make.exe` dentro de `%LOCALAPPDATA%\Microsoft\WinGet\Packages`, añade a `~/.bashrc` la carpeta que lo contiene y abre otra terminal:

  ```sh
  export PATH="<carpeta-que-contiene-make.exe>:$PATH"
  ```

  WSL2 es una alternativa si el equipo ya la utiliza: permite trabajar con `make`, Bash y Docker desde un entorno Linux, pero no es obligatoria para usar esta plantilla en Windows.
- **GitHub CLI** 2.94 o superior (las anteriores no tienen `--parent` ni `--blocked-by`), autenticado con permiso de escritura en Issues, etiquetas y PRs. Inicia sesión con `gh auth login` y compruébala con:

  ```sh
  gh auth status
  ```
- **Node.js** 22.20 o superior y **OpenSpec**, en la versión fijada en `.github/workflows/ci.yml` (`OPENSPEC_VERSION`). La primera vez en cada máquina, elige también el perfil con las etapas que usa este flujo, `verify` incluida:

  ```sh
  npm install -g @fission-ai/openspec@2.1.0
  openspec config set profile custom
  openspec config set workflows '["propose","explore","apply","update","verify","sync","archive"]'
  ```

Al adoptar la plantilla, genera las skills de OpenSpec para OpenCode y Codex:

```sh
openspec init --tools opencode,codex --scope project
```

Las skills quedan en `.agents/skills/` y se versionan con el proyecto. En clones posteriores, si ya están presentes y actualizadas, no hace falta volver a inicializarlas. Lo que necesita cada servicio en local está en [docs/ARCHITECTURE.md §7](docs/ARCHITECTURE.md#7-entorno-local-y-operación).

Comprueba las herramientas antes de continuar:

```sh
git --version
make --version
docker --version
gh auth status
node --version
npm --version
openspec --version
```

### Herramientas de IA

Las reglas están en [`AGENTS.md`](AGENTS.md); los procedimientos, en las skills de [`.agents/skills/`](.agents/skills/), y los subagentes, en [`.agents/agents/`](.agents/agents/). Cada herramienta tiene su adaptador, con sus subagentes y sus permisos:

| Herramienta | Instrucciones y skills | Subagentes | Permisos |
|---|---|---|---|
| OpenCode | `AGENTS.md` y `.agents/skills/` | `.opencode/agents/` | `opencode.jsonc` |
| Codex | `AGENTS.md` y `.agents/skills/` | `.codex/agents/` | `.codex/rules/`, si marcas el proyecto como de confianza |
| Claude Code | `CLAUDE.md` y `.claude/skills/` | `.claude/agents/` | `.claude/settings.json` |

Claude Code no lee `AGENTS.md` ni `.agents/skills/`: si lo usas, crea un `CLAUDE.md` con la línea `@AGENTS.md` y ejecuta `make claude-skills`, que copia las skills a `.claude/skills/`. Vuelve a ejecutarlo cuando cambien.

Los permisos impiden que la IA mergee PRs, haga push a `main`, fuerce un push o publique tags y releases, y le hacen pedir confirmación antes de un push a `dev` ([AGENTS §3](AGENTS.md#3-autonomía-y-límites)). Son archivos del repositorio: solo aplican al trabajar en él y no cambian tu configuración global. Son un freno para la IA, no una barrera; la protección real es la de las ramas en GitHub ([CONTRIBUTING §3](CONTRIBUTING.md#protección-de-ramas)).

### Arranque

Tras instalar las herramientas, configurar OpenSpec e inicializar sus skills, prepara el clon:

```sh
make setup   # prepara el clon: hooks de git, archivos .env e instalación
make up      # levanta todo con Docker
make help    # todos los comandos
```

### Demo en local

`make up` levanta `backend`, `worker`, `maintenance`, `frontend` y `db` en modo desarrollo. La web queda en <http://localhost:5173> y la API en <http://localhost:8000>. Entra con un usuario de prueba (el docente puede subir clases), sube un audio admitido por el [contrato](docs/CONTRACTS/coteach-ai-api.md) y sigue su avance hasta la transcripción por persona hablante. El análisis pedagógico sale vacío hasta E4. Antes de la primera clase hay que descargar los modelos (abajo).

Con la configuración de producción, backend, worker y maintenance requieren un `AUTH_SECRET` propio de al menos 32 caracteres; no aceptan el secreto documentado para desarrollo. Guárdalo solo en el `.env` sin versionar de este clon o pásalo desde la shell. Puedes generar uno localmente sin mostrarlo con `openssl rand -hex 32`. El emisor de tokens de prueba está apagado; para una demo local, actívalo de forma explícita al levantarla. La web queda en el puerto `FRONTEND_PORT` del `.env` de la raíz (5173 en el de ejemplo; 8080 si no está):

```sh
AUTH_SECRET="$(openssl rand -hex 32)" AUTH_DEV_ISSUER=true make up-prod
make down-prod
```

#### Modelos de inferencia

El worker transcribe con faster-whisper `small` y diariza con pyannote Community-1, en CPU y sin red: lee los modelos del volumen privado `models-data` (`MODELS_DIR`, `/app/data/models`) y nunca los descarga mientras procesa una clase ([ADR-0003](docs/ADR/0003-private-inference.md)). Su imagen (objetivo `worker` del `Dockerfile` de `backend`) lleva PyTorch para CPU y ocupa unos 3,4 GB, así que el primer `make up` tarda varios minutos más. Para preparar los modelos, una vez por equipo:

1. Crea una cuenta en [Hugging Face](https://huggingface.co), abre [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) y acepta sus condiciones de uso.
2. Crea un token de lectura en <https://huggingface.co/settings/tokens> y ponlo en `backend/.env` como `HF_TOKEN=...`. Ese archivo no se versiona ni entra en ninguna imagen. Compose pasa al worker `HF_TOKEN` vacío; en desarrollo `backend/` está montado en el contenedor, y de ahí lo lee `make models`, pero el worker no lo usa al procesar. Con `make up-prod`, el worker no tiene el archivo.
3. Ejecuta `make models`: descarga las revisiones fijadas de los dos modelos al volumen (unos 500 MB). Solo hace falta repetirlo si cambia una revisión o borras el volumen.

Sin modelos, cada trabajo falla con `processing_unavailable`, agota sus intentos (esperas de 60 y 120 s) y termina en `failed`. Para trabajar sin modelos, por ejemplo en el frontend, pon `INFERENCE_PIPELINE=fake` en `backend/.env` y vuelve a levantar con `make up`: el worker devuelve el resultado sintético del walking skeleton.

#### Prueba de extremo a extremo

La prueba E2E recorre la demo con Playwright en tu equipo, contra lo que esté levantado y con los modelos descargados. Antes de abrir el navegador, `make e2e` comprueba que los modelos están en el volumen y genera con espeak-ng una clase sintética de dos voces que se turnan (`backend/scripts/two-voices.sh`, en la imagen de desarrollo del worker). Ese audio no se versiona ni contiene datos reales. La prueba sube esa clase y espera su transcripción con dos personas hablantes; sube también un tono sin voz y espera el aviso de que no se ha detectado voz. En CPU, cada clase tarda unos minutos.

```sh
make e2e-install   # una vez por equipo: descarga Chromium
make e2e           # contra make up o make up-prod, con los puertos del .env de la raíz
```

El audio original se guarda en el volumen con nombre `audio-data`, montado en `/app/data/audio` en `backend`, `worker` y `maintenance`. No está dentro de Git ni se incluye en copias de seguridad. Con `make up` o `make up-prod`, la ruta del montaje la fija `AUDIO_STORAGE_DIR` en el `.env` de la raíz, como ruta absoluta dentro del contenedor; el mismo valor se pasa a los tres servicios. La imagen de producción solo prepara permisos para la ruta por defecto `/app/data/audio`: si se cambia, hay que asegurar que el nuevo punto de montaje sea escribible por el usuario `app` (uid 10001). `backend/.env` sigue usando `data/audio` para ejecutar el servicio sin Compose. El plazo de conservación se configura con `AUDIO_RETENTION_DAYS` en `backend/.env`.

Para comprobar la purga sin esperar 14 días, edita `backend/.env` con `AUDIO_RETENTION_DAYS=0.001` (unas 86 segundos) y `MAINTENANCE_INTERVAL_SECONDS=5`, y levanta de nuevo con `make up`. Sube una clase y detén el worker (`docker compose stop worker`) para que el trabajo quede sin terminar: en el siguiente ciclo, `maintenance` lo deja en `expired` y borra el audio del volumen. Recuerda restaurar los valores después. La web y la API no fijan ese plazo: el servicio es quien decide.

## Contribuir

- [`WORKFLOW.md`](WORKFLOW.md): el flujo de trabajo de principio a fin y el mapa de documentación.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): ramas, commits, Issues, PRs y versiones.
- [`AGENTS.md`](AGENTS.md): instrucciones para agentes de IA.

## Licencia

Sin licencia definida.
