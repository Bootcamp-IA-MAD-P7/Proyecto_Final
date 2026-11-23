# Revisión previa a publicación de Issues

Estado: material local de sincronización de Issues. Repositorio oficial Bootcamp-IA-MAD-P7/Proyecto_Final. La migración inicial se conserva por separado en `docs/migration-record/`.

## Comprobaciones

- Issues abiertas/cerradas: **0**; lista completa vacía, sin duplicados ni épicas existentes.
- Rama por defecto remota: dev. No se ejecutó Git para comprobar/cambiar checkout.
- GitHub CLI 2.96.0: soporta --parent, --blocked-by, --add-blocked-by, --body-file y comandos Project.
- Autenticación válida como mariaherrerosanchez; scopes repo, project, read:org, workflow, gist. Permisos del repositorio admin/maintain/push/triage/pull. Suficientes según metadata para operaciones propuestas; no se probó escritura.
- La consulta restringida inicial falló; consulta de red de solo lectura posterior confirmó sesión válida. No hace falta reautenticación.
- Projects vinculados al repositorio: ninguno (repository.projectsV2 vacío). Projects personales existentes: ComiSIA #1, MAREA #2, ESCENIQ #3; no se modificarán.
- Labels existentes: accessibility, bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix, feature, fix, refactor, docs, test, chore, epic, story, priority: high, priority: medium, priority: low, no-spec, needs: clarification, needs: triage, ready.
- Faltan únicamente las cinco etiquetas propuestas usadas en las fichas: area:backend, area:inference, area:frontend, area:devops, scope:mvp. No eliminar ni renombrar las existentes; no añadir labels de estado.

## Las 24 Issues propuestas

Los archivos enlazados contienen íntegra la ficha de origen, más metadata resuelta, DoD común y decisiones pendientes. Se conservan 76 escenarios Given/When/Then. Todas empiezan en Backlog, sin assignee. A/B/C solo son propuestas en el cuerpo. Los enlaces a dev deberán comprobarse antes de publicar: no se ha acreditado que la versión local del catálogo esté publicada.

| ID y cuerpo completo | Título | Épica | Hito | Propuesta |
|---|---|---|---|---|
| [US-001](US-001.md) | US-001 — Contrato versionado | E1 | Demo 11/12 | A |
| [US-002](US-002.md) | US-002 — Conformidad API | E1 | Demo 11/12 | C |
| [US-003](US-003.md) | US-003 — Conformidad de inferencia | E1 | Demo 11/12 | B |
| [US-004](US-004.md) | US-004 — Conformidad de interfaz | E1 | Demo 11/12 | C |
| [US-005](US-005.md) | US-005 — Integración del contrato | E1 | Demo 11/12 | C |
| [US-006](US-006.md) | US-006 — Skeleton desplegado | E1 | Demo 11/12 | A |
| [US-007](US-007.md) | US-007 — CI e integración del skeleton | E1 | Demo 11/12 | C |
| [US-008](US-008.md) | US-008 — Carga durable e idempotente | E2 | Demo 11/12 | A |
| [US-009](US-009.md) | US-009 — Ejecución y recuperación de trabajos | E2 | Demo 11/12 | A |
| [US-010](US-010.md) | US-010 — Integración de recepción | E2 | Demo 11/12 | C |
| [US-011](US-011.md) | US-011 — Transcripción normalizada | E3 | Demo 11/12 | B |
| [US-012](US-012.md) | US-012 — Diarización e integración de hablantes | E3 | Demo 11/12 | B |
| [US-013](US-013.md) | US-013 — Repaso y resumen general | E4 | Demo 11/12 | B |
| [US-014](US-014.md) | US-014 — Evaluación e integración pedagógica | E4 | Demo 11/12 | B |
| [US-015](US-015.md) | US-015 — Persistencia y consulta de versiones | E5 | Demo 11/12 | A |
| [US-016](US-016.md) | US-016 — Integración de acceso por clase | E5 | Demo 11/12 | A |
| [US-017](US-017.md) | US-017 — Corrección docente versionada | E6 | Demo 11/12 | C |
| [US-018](US-018.md) | US-018 — Aprobación y publicación programada | E6 | Demo 11/12 | A |
| [US-019](US-019.md) | US-019 — Integración de revisión y reloj | E6 | Demo 11/12 | C |
| [US-020](US-020.md) | US-020 — Carga y seguimiento en la interfaz web React | E7 | Demo 11/12 | C |
| [US-021](US-021.md) | US-021 — Revisión docente y consulta en la interfaz web React | E7 | Demo 11/12 | C |
| [US-022](US-022.md) | US-022 — Integración E2E de React con FastAPI | E7 | Demo 11/12 | C |
| [US-023](US-023.md) | US-023 — Consentimiento, purga y aislamiento | E8 | Demo 11/12 | A |
| [US-024](US-024.md) | US-024 — Ensayo E2E y capacidad de entrega | E8 | Entrega 15/12 | C |

## Revisión de workflow y relaciones

WORKFLOW §5 y la skill issues exigen specs/tasks aprobados antes de publicar historias. Solo US-001–005 disponen de secciones en el cambio existente, aún pendiente; las restantes no tienen cambios funcionales creados. No se autoriza apply ni se declara Ready. Si se decide publicarlas ahora como catálogo en Backlog antes de completar esos planes, la autorización debe reconocer expresamente esa excepción al orden del workflow. La petición actual exige cuerpos completos y prevalece sobre la plantilla que normalmente solo enlaza tasks; estos cuerpos no deben convertirse en una segunda fuente de avance.

Jerarquía propuesta: ocho épicas E1–E8, con agrupación de la tabla. No existen aún Issues padre. Crearlas supondría **8 Issues adicionales**, no incluidas en las 24; requiere autorización expresa. Los comandos de las 24 funcionan sin padre; la jerarquía se añadirá cuando existan épicas aprobadas. No inventar números.

No trasladar todas las dependencias de cierre a blocked-by: 008 menciona verificación 016 y 016 depende de 008; 015/016 presentan el mismo problema. Son integración y verificación cruzada, no un DAG de inicio. Se propone este mapa conservador sin ciclos. Para 017/018/023, preparación contra interfaces puede avanzar antes, pero sus relaciones se usan para iniciar implementación integrada, no para bloquear redacción de fixtures. Las dependencias de cierre íntegras permanecen en cada cuerpo.

| Historia | Bloqueos nativos propuestos (IDs provisionales) |
|---|---|
| US-001 | — |
| US-002 | US-001 |
| US-003 | US-001 |
| US-004 | US-001 |
| US-005 | US-001, US-002, US-003, US-004 |
| US-006 | US-001 |
| US-007 | US-006 |
| US-008 | US-001, US-006 |
| US-009 | US-001, US-006 |
| US-010 | US-008, US-009 |
| US-011 | US-001, US-006 |
| US-012 | US-009, US-011 |
| US-013 | US-001, US-006 |
| US-014 | US-012, US-013 |
| US-015 | US-001, US-006 |
| US-016 | US-001, US-008, US-015 |
| US-017 | US-001, US-015, US-016 |
| US-018 | US-017 |
| US-019 | US-015, US-016, US-017, US-018 |
| US-020 | US-001, US-004, US-006 |
| US-021 | US-004, US-020 |
| US-022 | US-010, US-014, US-016, US-019, US-020, US-021, US-023 |
| US-023 | US-001, US-006, US-008, US-009, US-016 |
| US-024 | US-014, US-022, US-023 |

US-022 incluye 023 y 014: no se cierra demo sin privacidad ni inferencia real. US-024 requiere cierre de todas las historias previas según su ficha. Decisiones Lay/ADR no se convierten en Issues ficticias; permanecen bloqueos descritos y no se marcan resueltas.

## Kanban propuesto

Nuevo Project privado **CoTeach-AI — MVP diciembre**, vinculado al repositorio. Reutilizar el campo estándar Status y configurar opciones, en orden: Backlog → Ready → In Progress → In Review → Done. No crear otro campo de estado. Vista Board agrupada por Status; campo Hito objetivo con Demo 11/12 y Entrega 15/12. Conservar Priority en labels existentes, sin duplicarlo obligatoriamente como campo.

CLI permite crear/vincular Project, campos e ítems y fijar valores; no ofrece subcomando para editar opciones del campo existente ni configurar vista Board. Se preparan esos pasos en interfaz web: abrir Project, Settings/Status, establecer las cinco opciones; crear o cambiar vista a Board agrupada por Status; revisar automatizaciones para que no asignen Ready/In Progress a nuevos ítems. Después leer IDs reales y establecer Backlog explícitamente. No asumir número de Project ni IDs. Ninguna acción UI se ejecutó en este encargo.

## Comandos previstos (Git Bash; NO ejecutados)

Ejecutar desde la raíz solo después de autorización y nueva comprobación de duplicados. No es un script idempotente: si una creación falla, detenerse, registrar URLs creadas y reconciliar antes de reanudar; nunca repetir todo el bloque ciegamente. Cada comando de creación de Issue está protegido con salida por error. Guardar el mapa US→URL durante publicación.

```bash
REPO='Bootcamp-IA-MAD-P7/Proyecto_Final'
OWNER='mariaherrerosanchez'
BODY_DIR='docs/issue-publication'
gh issue list --repo "$REPO" --state all --limit 200 --json number,title,url
gh label list --repo "$REPO" --limit 200 --json name
```

Crear solo las cinco ausentes tras revisión; sin --force para no sobrescribir:

```bash
gh label create 'area:backend' --repo "$REPO" --color '1D76DB' --description 'API, dominio y persistencia' || exit 1
gh label create 'area:inference' --repo "$REPO" --color '5319E7' --description 'Transcripción, diarización y análisis' || exit 1
gh label create 'area:frontend' --repo "$REPO" --color '0E8A16' --description 'Interfaz y cliente de API' || exit 1
gh label create 'area:devops' --repo "$REPO" --color 'C5DEF5' --description 'Entornos, despliegue y CI' || exit 1
gh label create 'scope:mvp' --repo "$REPO" --color 'FBCA04' --description 'Alcance del MVP de diciembre' || exit 1
```

Estas nuevas categorías deberán registrarse posteriormente en ISSUE_LABELS mediante un cambio autorizado; no se modifica ese documento ahora ni se ejecuta make labels (actualizaría más etiquetas).

```bash
PROJECT_JSON=$(gh project create --owner "$OWNER" --title 'CoTeach-AI — MVP diciembre' --format json) || exit 1
PROJECT_NUMBER=$(printf '%s' "$PROJECT_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["number"])')
PROJECT_ID=$(printf '%s' "$PROJECT_JSON" | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
gh project link "$PROJECT_NUMBER" --owner "$OWNER" --repo "$REPO" || exit 1
gh project field-create "$PROJECT_NUMBER" --owner "$OWNER" --name 'Hito objetivo' --data-type SINGLE_SELECT --single-select-options 'Demo 11/12,Entrega 15/12' || exit 1
gh project view "$PROJECT_NUMBER" --owner "$OWNER" --web
# Pausa operativa: configurar Status y vista Board según pasos anteriores.
gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json
```

A partir de la salida anterior, rellenar STATUS_FIELD_ID, BACKLOG_OPTION_ID, HITO_FIELD_ID, DEMO_OPTION_ID y DELIVERY_OPTION_ID con IDs reales verificados; no son valores conocidos antes de crear el Project. Reanudar solo tras verificar opciones y configuración. No existe un comando gh project para configurar Board; ese paso web queda incluido en la autorización futura.

```bash
declare -A ISSUE_URL ITEM_ID
ISSUE_URL[US-001]=$(gh issue create --repo "$REPO" --title 'US-001 — Contrato versionado' --body-file "$BODY_DIR/US-001.md" --label 'story' --label 'docs' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-002]=$(gh issue create --repo "$REPO" --title 'US-002 — Conformidad API' --body-file "$BODY_DIR/US-002.md" --label 'story' --label 'test' --label 'priority: medium' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-003]=$(gh issue create --repo "$REPO" --title 'US-003 — Conformidad de inferencia' --body-file "$BODY_DIR/US-003.md" --label 'story' --label 'test' --label 'priority: medium' --label 'area:inference' --label 'scope:mvp') || exit 1
ISSUE_URL[US-004]=$(gh issue create --repo "$REPO" --title 'US-004 — Conformidad de interfaz' --body-file "$BODY_DIR/US-004.md" --label 'story' --label 'test' --label 'priority: medium' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-005]=$(gh issue create --repo "$REPO" --title 'US-005 — Integración del contrato' --body-file "$BODY_DIR/US-005.md" --label 'story' --label 'test' --label 'priority: medium' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-006]=$(gh issue create --repo "$REPO" --title 'US-006 — Skeleton desplegado' --body-file "$BODY_DIR/US-006.md" --label 'story' --label 'chore' --label 'priority: high' --label 'area:devops' --label 'scope:mvp') || exit 1
ISSUE_URL[US-007]=$(gh issue create --repo "$REPO" --title 'US-007 — CI e integración del skeleton' --body-file "$BODY_DIR/US-007.md" --label 'story' --label 'chore' --label 'priority: high' --label 'area:devops' --label 'scope:mvp') || exit 1
ISSUE_URL[US-008]=$(gh issue create --repo "$REPO" --title 'US-008 — Carga durable e idempotente' --body-file "$BODY_DIR/US-008.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-009]=$(gh issue create --repo "$REPO" --title 'US-009 — Ejecución y recuperación de trabajos' --body-file "$BODY_DIR/US-009.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-010]=$(gh issue create --repo "$REPO" --title 'US-010 — Integración de recepción' --body-file "$BODY_DIR/US-010.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-011]=$(gh issue create --repo "$REPO" --title 'US-011 — Transcripción normalizada' --body-file "$BODY_DIR/US-011.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:inference' --label 'scope:mvp') || exit 1
ISSUE_URL[US-012]=$(gh issue create --repo "$REPO" --title 'US-012 — Diarización e integración de hablantes' --body-file "$BODY_DIR/US-012.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:inference' --label 'scope:mvp') || exit 1
ISSUE_URL[US-013]=$(gh issue create --repo "$REPO" --title 'US-013 — Repaso y resumen general' --body-file "$BODY_DIR/US-013.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:inference' --label 'scope:mvp') || exit 1
ISSUE_URL[US-014]=$(gh issue create --repo "$REPO" --title 'US-014 — Evaluación e integración pedagógica' --body-file "$BODY_DIR/US-014.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:inference' --label 'scope:mvp') || exit 1
ISSUE_URL[US-015]=$(gh issue create --repo "$REPO" --title 'US-015 — Persistencia y consulta de versiones' --body-file "$BODY_DIR/US-015.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-016]=$(gh issue create --repo "$REPO" --title 'US-016 — Integración de acceso por clase' --body-file "$BODY_DIR/US-016.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-017]=$(gh issue create --repo "$REPO" --title 'US-017 — Corrección docente versionada' --body-file "$BODY_DIR/US-017.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-018]=$(gh issue create --repo "$REPO" --title 'US-018 — Aprobación y publicación programada' --body-file "$BODY_DIR/US-018.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-019]=$(gh issue create --repo "$REPO" --title 'US-019 — Integración de revisión y reloj' --body-file "$BODY_DIR/US-019.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-020]=$(gh issue create --repo "$REPO" --title 'US-020 — Carga y seguimiento en la interfaz web React' --body-file "$BODY_DIR/US-020.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-021]=$(gh issue create --repo "$REPO" --title 'US-021 — Revisión docente y consulta en la interfaz web React' --body-file "$BODY_DIR/US-021.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-022]=$(gh issue create --repo "$REPO" --title 'US-022 — Integración E2E de React con FastAPI' --body-file "$BODY_DIR/US-022.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:frontend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-023]=$(gh issue create --repo "$REPO" --title 'US-023 — Consentimiento, purga y aislamiento' --body-file "$BODY_DIR/US-023.md" --label 'story' --label 'feature' --label 'priority: high' --label 'area:backend' --label 'scope:mvp') || exit 1
ISSUE_URL[US-024]=$(gh issue create --repo "$REPO" --title 'US-024 — Ensayo E2E y capacidad de entrega' --body-file "$BODY_DIR/US-024.md" --label 'story' --label 'test' --label 'priority: high' --label 'area:inference' --label 'scope:mvp') || exit 1

for US in US-001 US-002 US-003 US-004 US-005 US-006 US-007 US-008 US-009 US-010 US-011 US-012 US-013 US-014 US-015 US-016 US-017 US-018 US-019 US-020 US-021 US-022 US-023 US-024; do
  ITEM_ID[$US]=$(gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "${ISSUE_URL[$US]}" --format json --jq '.id') || exit 1
  gh project item-edit --id "${ITEM_ID[$US]}" --project-id "$PROJECT_ID" --field-id "$STATUS_FIELD_ID" --single-select-option-id "$BACKLOG_OPTION_ID" || exit 1
  HITO_OPTION_ID="$DEMO_OPTION_ID"
  if [ "$US" = 'US-024' ]; then HITO_OPTION_ID="$DELIVERY_OPTION_ID"; fi
  gh project item-edit --id "${ITEM_ID[$US]}" --project-id "$PROJECT_ID" --field-id "$HITO_FIELD_ID" --single-select-option-id "$HITO_OPTION_ID" || exit 1
done
gh issue edit "${ISSUE_URL[US-002]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-003]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-004]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-005]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-005]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-002]}" || exit 1
gh issue edit "${ISSUE_URL[US-005]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-003]}" || exit 1
gh issue edit "${ISSUE_URL[US-005]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-004]}" || exit 1
gh issue edit "${ISSUE_URL[US-006]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-007]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-008]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-008]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-009]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-009]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-010]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-008]}" || exit 1
gh issue edit "${ISSUE_URL[US-010]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-009]}" || exit 1
gh issue edit "${ISSUE_URL[US-011]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-011]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-012]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-009]}" || exit 1
gh issue edit "${ISSUE_URL[US-012]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-011]}" || exit 1
gh issue edit "${ISSUE_URL[US-013]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-013]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-014]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-012]}" || exit 1
gh issue edit "${ISSUE_URL[US-014]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-013]}" || exit 1
gh issue edit "${ISSUE_URL[US-015]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-015]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-016]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-016]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-008]}" || exit 1
gh issue edit "${ISSUE_URL[US-016]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-015]}" || exit 1
gh issue edit "${ISSUE_URL[US-017]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-017]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-015]}" || exit 1
gh issue edit "${ISSUE_URL[US-017]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-016]}" || exit 1
gh issue edit "${ISSUE_URL[US-018]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-017]}" || exit 1
gh issue edit "${ISSUE_URL[US-019]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-015]}" || exit 1
gh issue edit "${ISSUE_URL[US-019]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-016]}" || exit 1
gh issue edit "${ISSUE_URL[US-019]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-017]}" || exit 1
gh issue edit "${ISSUE_URL[US-019]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-018]}" || exit 1
gh issue edit "${ISSUE_URL[US-020]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-020]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-004]}" || exit 1
gh issue edit "${ISSUE_URL[US-020]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-021]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-004]}" || exit 1
gh issue edit "${ISSUE_URL[US-021]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-020]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-010]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-014]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-016]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-019]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-020]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-021]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-023]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-001]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-006]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-008]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-009]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-016]}" || exit 1
gh issue edit "${ISSUE_URL[US-024]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-014]}" || exit 1
gh issue edit "${ISSUE_URL[US-024]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-022]}" || exit 1
gh issue edit "${ISSUE_URL[US-024]}" --repo "$REPO" --add-blocked-by "${ISSUE_URL[US-023]}" || exit 1
```

Jerarquía condicional, solo tras disponer de las ocho épicas autorizadas: definir EPIC_URL[E1]…EPIC_URL[E8] con URLs reales. Comandos previstos:

```bash
gh issue edit "${ISSUE_URL[US-001]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-002]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-003]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-004]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-005]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-006]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-007]}" --repo "$REPO" --parent "${EPIC_URL[E1]}" || exit 1
gh issue edit "${ISSUE_URL[US-008]}" --repo "$REPO" --parent "${EPIC_URL[E2]}" || exit 1
gh issue edit "${ISSUE_URL[US-009]}" --repo "$REPO" --parent "${EPIC_URL[E2]}" || exit 1
gh issue edit "${ISSUE_URL[US-010]}" --repo "$REPO" --parent "${EPIC_URL[E2]}" || exit 1
gh issue edit "${ISSUE_URL[US-011]}" --repo "$REPO" --parent "${EPIC_URL[E3]}" || exit 1
gh issue edit "${ISSUE_URL[US-012]}" --repo "$REPO" --parent "${EPIC_URL[E3]}" || exit 1
gh issue edit "${ISSUE_URL[US-013]}" --repo "$REPO" --parent "${EPIC_URL[E4]}" || exit 1
gh issue edit "${ISSUE_URL[US-014]}" --repo "$REPO" --parent "${EPIC_URL[E4]}" || exit 1
gh issue edit "${ISSUE_URL[US-015]}" --repo "$REPO" --parent "${EPIC_URL[E5]}" || exit 1
gh issue edit "${ISSUE_URL[US-016]}" --repo "$REPO" --parent "${EPIC_URL[E5]}" || exit 1
gh issue edit "${ISSUE_URL[US-017]}" --repo "$REPO" --parent "${EPIC_URL[E6]}" || exit 1
gh issue edit "${ISSUE_URL[US-018]}" --repo "$REPO" --parent "${EPIC_URL[E6]}" || exit 1
gh issue edit "${ISSUE_URL[US-019]}" --repo "$REPO" --parent "${EPIC_URL[E6]}" || exit 1
gh issue edit "${ISSUE_URL[US-020]}" --repo "$REPO" --parent "${EPIC_URL[E7]}" || exit 1
gh issue edit "${ISSUE_URL[US-021]}" --repo "$REPO" --parent "${EPIC_URL[E7]}" || exit 1
gh issue edit "${ISSUE_URL[US-022]}" --repo "$REPO" --parent "${EPIC_URL[E7]}" || exit 1
gh issue edit "${ISSUE_URL[US-023]}" --repo "$REPO" --parent "${EPIC_URL[E8]}" || exit 1
gh issue edit "${ISSUE_URL[US-024]}" --repo "$REPO" --parent "${EPIC_URL[E8]}" || exit 1
```

Verificación posterior prevista, de lectura:

```bash
gh issue list --repo "$REPO" --state all --limit 200 --json number,title,labels,assignees,url
gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 100 --format json
gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json
```

Comprobar 24 historias, cuerpos íntegros, labels correctas, Backlog en todas, cero assignees, hitos 23/1, enlaces y dependencias; verificar padres solo si se autorizó crear/enlazar épicas. La aprobación solicitada es de este paquete concreto, no de los documentos de producto/técnica pendientes.

