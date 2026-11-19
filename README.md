<!-- Plantilla: sustituye los textos entre corchetes. Si acabas de crear el repositorio, sigue setup/README.md y borra este comentario al terminar. -->

# [Nombre del proyecto]

[Qué es y para quién, en una o dos frases.] Más contexto en [`docs/PRD.md`](docs/PRD.md).

## Estado

El trabajo se sigue en [GitHub Issues](https://github.com/[owner]/[repo]/issues) y las versiones se publican en [Releases](https://github.com/[owner]/[repo]/releases).

## Puesta en marcha

### Herramientas

- **Docker** y **make**. En Windows, trabaja dentro de WSL2, la misma base que usa Docker Desktop: clona el repositorio en WSL y ahí `make`, `bash` y Docker funcionan como en Linux.
- **GitHub CLI** 2.94 o superior (las anteriores no tienen `--parent` ni `--blocked-by`), autenticado con permiso de escritura en Issues, etiquetas y PRs: `gh auth login`.
- **Node.js** 22.20 o superior y **OpenSpec**, en la versión fijada en `.github/workflows/ci.yml` (`OPENSPEC_VERSION`). La primera vez en cada máquina, elige también el perfil con las etapas que usa este flujo, `verify` incluida:

  ```sh
  npm install -g @fission-ai/openspec@2.1.0
  openspec config set profile custom
  openspec config set workflows '["propose","explore","apply","update","verify","sync","archive"]'
  ```

Las skills de OpenSpec están en el repositorio, en `.agents/skills/`, así que no hace falta `openspec init`. Lo que necesita cada servicio en local está en [docs/ARCHITECTURE.md §7](docs/ARCHITECTURE.md#7-entorno-local-y-operación).

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

```sh
make setup   # prepara el clon: hooks de git, archivos .env e instalación
make up      # levanta todo con Docker
make help    # todos los comandos
```

## Contribuir

- [`WORKFLOW.md`](WORKFLOW.md): el flujo de trabajo de principio a fin y el mapa de documentación.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): ramas, commits, Issues, PRs y versiones.
- [`AGENTS.md`](AGENTS.md): instrucciones para agentes de IA.

## Licencia

[Licencia, o «Sin licencia definida».]
