# CONTRIBUTING

Convenciones para personas y agentes de IA. El flujo y sus paradas están en [`WORKFLOW.md`](WORKFLOW.md); las reglas propias de la IA, en [`AGENTS.md`](AGENTS.md).

## 1. Idioma

- **Inglés:** todo lo que es código o lo nombra: código y sus comentarios, identificadores, funciones, nombres de archivos y carpetas (también los de documentación), servicios, variables de entorno, objetivos del Makefile, ramas, commits y etiquetas.
- **Español:** lo que explica el proyecto a las personas: documentación, Issues, PRs, artefactos de OpenSpec e instrucciones para la IA, salvo las palabras clave de formato que valida el CLI (encabezados, `SHALL`/`MUST`, `WHEN`/`THEN`).

## 2. Modelo de trabajo

```text
Épica                 (Issue · epic; agrupada por hitos en docs/ROADMAP.md)
└── Funcionalidad     (un cambio de OpenSpec: propuesta, specs, diseño y tasks.md)
    └── Historia      (Issue · story · sub-issue de la épica = una sección de tasks.md)
        └── [ ] tarea (casilla de esa sección)
```

- **Épica:** capacidad de producto acotada. Se cierra con el PR de integración de su última funcionalidad (`Closes #E`).
- **Funcionalidad:** bloque coherente de una épica que aporta valor por sí solo y la unidad de especificación. **Una funcionalidad = un cambio de OpenSpec**, que se planifica entero con `propose` y se archiva en el PR de su última sección, la de integración. Una épica pequeña es una sola funcionalidad; una grande se reparte en varias. Como referencia, una funcionalidad tiene hasta unas cinco historias de una o dos capacidades relacionadas. No es una Issue: vive en `openspec/changes/` y se enlaza desde su épica en el ROADMAP.
- **Historia:** una sección de `tasks.md` de su funcionalidad: un incremento pequeño y observable de una capa (o de un contrato) que la deja funcionando. Se crea a partir del plan aprobado. **Una historia = una rama = un PR**; las historias de una funcionalidad comparten su cambio de OpenSpec.
- **Historia suelta:** bug o mejora fuera de una épica en curso. Lleva su propio cambio pequeño, salvo que tenga la etiqueta `no-spec` ([WORKFLOW §5](WORKFLOW.md#historias-sueltas)).
- **Tarea:** casilla de la sección de la historia en `tasks.md`, que es su fuente de verdad. No es una Issue ni lleva etiqueta.
- **Bug:** historia de tipo `fix`, con la plantilla de bug. Cuelga de una épica si pertenece a una.

Las historias se dividen por capas, con el contrato primero ([WORKFLOW §5](WORKFLOW.md#trabajo-por-capas)). La jerarquía (sub-issues) y los bloqueos (*blocked by*) se registran con las relaciones nativas de GitHub, que son su fuente de verdad. La jerarquía no implica orden: un bloqueo solo existe cuando una Issue no puede avanzar sin otra.

### Definición de Ready

Una historia está lista (`ready`) cuando:

- cuelga de su épica y su sección de `tasks.md` está en `dev` (el PR del plan de su funcionalidad está mergeado), o es una historia suelta;
- tiene criterios de aceptación observables y cita los requisitos que implementa (`RF`, `RNF`, `RD`) o explica por qué no aplica ninguno: en su sección de `tasks.md` o, si es una historia suelta, en la Issue;
- no tiene bloqueos abiertos.

### Definición de Done

Una historia está terminada cuando:

- el subagente reviewer no deja hallazgos abiertos dentro del alcance;
- `verify`, limitado a su sección, no deja discrepancias con los artefactos aprobados y `openspec validate` pasa (salvo `no-spec`);
- las casillas de su sección de `tasks.md` están marcadas;
- los tests y checks del proyecto pasan, en local y en el CI;
- la documentación afectada está actualizada ([WORKFLOW §2](WORKFLOW.md#qué-actualizar-cuando-algo-cambia));
- el PR está revisado, con `Closes #N`, y la persona lo ha mergeado en `dev`.

Una funcionalidad está terminada cuando todas sus historias lo están y su cambio de OpenSpec está archivado: `verify` sobre el cambio completo no deja discrepancias y las specs están sincronizadas. El archive es el último commit del PR de su sección de integración. Una épica está terminada cuando lo están todas sus funcionalidades; el PR de integración de la última lleva también `Closes #E`.

## 3. Ramas

```text
feature/*  ─┐
fix/*       │
refactor/*  ├──→ dev ───→ main
docs/*      │
test/*      │
chore/*    ─┘
```

- `main`: producción. Solo recibe promociones desde `dev`.
- `dev`: integración y rama por defecto del repositorio, para que `Closes #N` cierre las Issues al mergear en ella.
- Las ramas de trabajo salen de `dev` y vuelven a `dev` por PR; `dev` llega a `main` por un PR de promoción. No se hace push directo a `dev` ni a `main`.

Formato: `<tipo>/<issue>-<descripcion>` en kebab-case, por ejemplo `feature/12-briefing-form` o `fix/31-empty-response`. Solo el trabajo sin Issue omite el número, como `docs/update-roadmap`. El CI rechaza el PR si la rama no sigue el formato.

La única excepción a «no hay push directo a `dev`» es el commit de la definición inicial del proyecto ([WORKFLOW §4](WORKFLOW.md#4-fase-1--definición)), que se hace antes de proteger las ramas.

### Protección de ramas

Las reglas están en [`.github/rulesets/`](.github/rulesets/) y se aplican con `make github-protect` al terminar la definición inicial ([WORKFLOW §4](WORKFLOW.md#4-fase-1--definición)). Sin ellas, «no hay push directo» solo es una norma escrita.

- **`dev`:** PR obligatorio, solo *Rebase and merge*, historia lineal y los checks `Convenciones`, `OpenSpec` y `Servicios`.
- **`main`:** PR obligatorio, solo *Create a merge commit* y los checks `OpenSpec` y `Servicios`.
- **Las dos:** sin borrado ni *force push*, y 0 aprobaciones obligatorias, pensadas para una sola persona: súbelas si sois más.

Para cambiar una regla, edita su JSON en un PR `chore` y vuelve a ejecutar `make github-protect`, que actualiza las existentes. En repositorios privados con el plan Free, GitHub no aplica estas reglas: hace falta un repositorio público o un plan de pago.

## 4. Tipos de trabajo

El tipo se elige en la Issue y determina la rama y el tipo principal de commit:

| Etiqueta de la Issue | Rama | Commit principal |
|---|---|---|
| `feature`, `enhancement` | `feature/` | `feat` |
| `fix` | `fix/` | `fix` |
| `refactor` | `refactor/` | `refactor` |
| `docs` | `docs/` | `docs` |
| `test` | `test/` | `test` |
| `chore` | `chore/` | `chore` |

Una rama puede incluir commits de otros tipos (`test`, `docs`, `perf`, `ci`, `build`) cuando forman parte de la misma historia.

## 5. Commits

[Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/), sin prefijos propios:

```text
type(scope): description
```

- `type`: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci` o `build`.
- `scope`: opcional; el componente de [ARCHITECTURE §3](docs/ARCHITECTURE.md#3-componentes), el módulo o la capacidad afectada.
- `description`: en imperativo, en minúscula y sin punto final.
- Cambio incompatible: `!` tras el tipo (`feat(api)!: …`) y pie `BREAKING CHANGE: …`.
- Pie `Refs #N` cuando el commit pertenece a una historia.
- En inglés, también la descripción.

El CI comprueba el asunto de cada commit del PR, y el hook `.githooks/commit-msg` lo hace en local antes de crear el commit (se activa con `make setup`).

```text
feat(api): add generation endpoint
fix(editor): prevent empty submission
docs(specs): sync add-generation-endpoint
chore(openspec): archive add-generation-endpoint
```

Cada commit es un bloque lógico que se entiende y se revisa por sí solo. No mezcles componentes (frontend y backend, por ejemplo) ni código y documentación en el mismo commit.

## 6. Issues

- Plantillas en `.github/ISSUE_TEMPLATE/`: épica, historia y bug. Etiquetas en [`docs/ISSUE_LABELS.md`](docs/ISSUE_LABELS.md).
- Cada Issue lleva exactamente una etiqueta de nivel (`epic` o `story`) y al menos una de tipo.
- Las Issues de historia se crean a partir de las secciones de `tasks.md` del plan aprobado de su funcionalidad (skill `issues`), no antes, y enlazan su sección en lugar de copiarla. La Issue es la puerta de entrada al trabajo; el plan está en el cambio de OpenSpec.
- Historias y épicas se cierran con `Closes` al mergear su PR en `dev` (§7). Las descartadas se cierran como *not planned*, con un comentario que explique el motivo.

## 7. Pull requests

### Plan de una funcionalidad → `dev`

- Un PR por funcionalidad, desde la rama `docs/<épica>-<cambio>`, con el cambio de OpenSpec recién propuesto y su enlace en el ROADMAP ([WORKFLOW §5](WORKFLOW.md#trabajo-por-capas)).
- Lleva `Refs #E`: la épica sigue abierta hasta el PR de integración de su última funcionalidad. La revisión del plan ya se hizo en la Parada 2; la persona lo mergea con el CI en verde.

### Historia → `dev`

- Un PR por historia, con la plantilla de PR.
- Lleva `Closes #N` desde que se abre, para que GitHub cierre la historia al mergear; el CI comprueba que el cuerpo cite la Issue de la rama. El PR de la sección de integración añade tras la revisión el archive del cambio como últimos commits, y `Closes #E` si es la última funcionalidad de la épica ([WORKFLOW §6](WORKFLOW.md#6-fase-3--ejecución-de-una-historia)).
- Merge con **Rebase and merge**, para conservar los commits; squash fundiría el archive y los commits enfocados en uno solo.

### Promoción `dev` → `main`

- Indica la versión y lista las historias incluidas con `Refs #N`.
- Merge con **Create a merge commit**, para que `main` y `dev` no diverjan.

### Correcciones urgentes

Siguen el camino de cualquier historia (`fix/` → `dev`), seguido de una promoción inmediata. La promoción lleva también todo lo que haya en `dev`: si hay funcionalidades a medias, la IA lo avisa (skill `release`) y la persona decide entre publicarlas ya, porque cada historia deja su capa funcionando y probada, o esperar a terminarlas.

### Revisión

La persona revisa el PR y lo mergea con el CI en verde. Los agentes de IA no mergean.

## 8. Calidad y CI

El CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) comprueba en cada PR a `dev` la rama, los commits y la referencia a la Issue (`Convenciones`) y comenta la versión prevista (§9). En los PRs a `dev` y a `main`, valida OpenSpec (`OpenSpec`) y ejecuta `make ci` (`Servicios`): el lint y los tests de cada servicio en su imagen de desarrollo y la construcción de las imágenes de producción. Mientras no hay servicios, `Servicios` pasa sin hacer nada; cada servicio fija sus herramientas en su `Makefile` y su `Dockerfile` ([ARCHITECTURE §8](docs/ARCHITECTURE.md#8-calidad-tests-ci-y-observabilidad)).

La versión de OpenSpec está fijada en `ci.yml` (`OPENSPEC_VERSION`) y en el [README](README.md#herramientas). Se sube a propósito, en un PR `chore` propio, nunca con `@latest`: cambia las dos, ejecuta `openspec update` con el perfil del README y sube las skills que regenera en `.agents/skills/`.

### Prueba de extremo a extremo

La prueba E2E (Playwright contra lo levantado, con los modelos reales) no corre en el CI: necesita los modelos, un navegador y varios minutos de CPU por clase. Por eso la sección de integración de cada cambio ([WORKFLOW §5](WORKFLOW.md#trabajo-por-capas)) la ejecuta en local antes de abrir su PR: `make up`, `make e2e-install` una vez por equipo y `make e2e`. El resultado va en la «Validación» del PR. Cómo prepararla (modelos, audio sintético y puertos): [README](README.md#prueba-de-extremo-a-extremo).

## 9. Versiones y releases

Las versiones siguen [Semantic Versioning](https://semver.org/lang/es/) según los tipos de commit:

- `MAJOR`: cambio incompatible (`!` o `BREAKING CHANGE`). Mientras `MAJOR` sea 0, sube `MINOR`.
- `MINOR`: `feat`.
- `PATCH`: `fix` y `perf`.
- `docs`, `refactor`, `test`, `chore`, `ci` y `build` no cambian la versión.

La primera versión es `0.1.0`; la persona decide cuándo se publica `1.0.0`.

| Al mergear | Tag | Dónde | Release de GitHub |
|---|---|---|---|
| En `dev`, un PR que cambia la versión | `vX.Y.Z-beta.N` | Último commit de `dev` | No |
| En `main`, una promoción | `vX.Y.Z` | Commit de merge en `main` | Sí, con notas generadas desde el último tag estable |

- Los tags y las releases los crea el CI ([`.github/workflows/tags.yml`](.github/workflows/tags.yml)); no se crean a mano.
- **Revisión humana:** en cada PR a `dev`, el CI comenta el tag beta previsto y los commits que lo causan; la persona lo aprueba en la Parada 3 ([WORKFLOW §6](WORKFLOW.md#6-fase-3--ejecución-de-una-historia)). Si no es el esperado, se corrigen los tipos de commit antes del merge.
- **`X.Y.Z` del tag beta:** la siguiente versión estable según los commits desde el último tag estable, o `0.1.0` si no hay ninguno. **`N`** empieza en 1, sube con cada beta y vuelve a 1 cuando cambia `X.Y.Z`.
- **El tag estable** es el último tag beta sin el sufijo.
- No hay CHANGELOG manual: las notas de versión son las GitHub Releases.

## 10. Entorno de ejecución: Makefile, Docker y variables

### Makefile

- El `Makefile` de la raíz es la única entrada para los comandos del proyecto. `make help` los lista con su descripción, así que el README no los repite.
- Cada objetivo lleva un comentario `## descripción` en su línea para que aparezca en `make help`.
- Objetivos generales: `setup` (prepara el clon: hooks, `.env` e instalación de todo), `up`, `down` y `logs` (todo con Docker, en desarrollo), `up-prod` (todo con la configuración de producción), `test` y `lint` (en local), `ci` (lo que ejecuta el CI, en Docker), y `e2e-install` y `e2e` (la prueba de extremo a extremo en el equipo, contra lo levantado; §8). Los de configuración de GitHub y de las herramientas de IA también están en `make help`.
- Objetivos por servicio, con el nombre del servicio como prefijo: `<servicio>-install`, `<servicio>-dev` (solo ese servicio, en local sin Docker), `<servicio>-test`, `<servicio>-lint`, y `<servicio>-up`, `<servicio>-down` y `<servicio>-logs` (solo ese servicio, con Docker). `worker` y `maintenance` comparten `backend/`, así que sus logs tienen objetivos propios: `worker-logs` y `maintenance-logs`.
- Cada servicio vive en su carpeta con su propio `Makefile`, que define `install`, `dev`, `test` y `lint` para trabajar en local. El `Makefile` de la raíz detecta esas carpetas y genera los objetivos por servicio; no hay que tocarlo al añadir un servicio.
- Los nombres de los objetivos van en inglés y en kebab-case.

### Docker

- Docker se usa siempre que se pueda, para los servicios y para sus dependencias (base de datos, caché, colas…). Sin Docker solo se trabaja para iterar o probar en local; por ejemplo, SQLite en local y la imagen de PostgreSQL en Docker y en producción.
- Cada servicio tiene un `Dockerfile` multietapa con al menos los objetivos `dev` y `prod`.
- Con más de una imagen hay Docker Compose, en tres archivos con los nombres que usa Docker:
  - `compose.yaml`: la base común a todos los entornos.
  - `compose.override.yaml`: desarrollo. `docker compose up` lo combina con la base de forma automática.
  - `compose.production.yaml`: producción, con `docker compose -f compose.yaml -f compose.production.yaml up -d`.

### Variables de entorno

- `.env` en la raíz: lo usa Docker Compose para levantar todo junto (puertos, valores compartidos).
- `<servicio>/.env`: lo usa el servicio cuando se levanta solo, en local o con su imagen sin Compose.
- Solo se versionan los `.env.example`, con nombres y valores inocuos; `make setup` crea cada `.env` a partir de su ejemplo si no existe. Los nombres de las variables van en inglés y en `UPPER_SNAKE_CASE`.
