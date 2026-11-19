---
name: add-service
description: Cómo añadir un servicio al repositorio con su Makefile, Dockerfile, Compose, variables de entorno y punto de salud, listo para el CI. Úsala en el walking skeleton o cada vez que aparezca un servicio nuevo.
---

# Añadir un servicio

Convenciones en [CONTRIBUTING §10](../../../CONTRIBUTING.md#10-entorno-de-ejecución-makefile-docker-y-variables); qué incluye el *walking skeleton*, en [WORKFLOW §5](../../../WORKFLOW.md#trabajo-por-capas). Esta skill es el procedimiento.

1. **Nombre:** el del componente en ARCHITECTURE §3, en inglés y kebab-case (`api`, `web`, `worker`). Es también la carpeta, el servicio de Compose y el prefijo de sus objetivos de make.
2. **Carpeta** `<service>/` con el esqueleto mínimo del stack elegido y un punto de salud (por ejemplo, `GET /health`) con su test.
3. **`<service>/Makefile`** con los objetivos `install`, `dev`, `test` y `lint`, cada uno con su `## descripción`. El `Makefile` de la raíz lo detecta solo: no lo toques.
4. **`<service>/Dockerfile`** multietapa con al menos los objetivos `dev` y `prod`. La imagen `dev` incluye `make` y las herramientas de test y lint, y su directorio de trabajo contiene el `Makefile` del servicio: el CI ejecuta ahí `make lint test`.
5. **Compose:**
   - `compose.yaml`: el servicio con lo común (imagen, `env_file`, dependencias);
   - `compose.override.yaml`: `target: dev`, puertos y volúmenes para recarga en caliente;
   - `compose.production.yaml`: `target: prod` y la política de reinicio.
   Las dependencias (base de datos, caché, colas) van también como servicios de Compose.
6. **Variables:** `<service>/.env.example` con nombres en `UPPER_SNAKE_CASE` y valores inocuos, y lo compartido en el `.env.example` de la raíz. Nunca secretos reales.
7. **CI:** no hay que tocar `ci.yml`. El job `Servicios` ejecuta `make ci`, que pasa `make lint test` en la imagen `dev` de cada servicio y construye las de producción.
8. **Documentación:** ARCHITECTURE §3 (componente con estado Actual), §4 (estructura), §7 (requisitos previos y puertos) y §9 (despliegue) si cambia.
9. **Comprueba**, y no des el paso por hecho sin ejecutarlo:
   - `make setup` y `make help` muestran los objetivos `<service>-*`;
   - `make <service>-test` y `make <service>-lint` pasan;
   - `make ci` pasa, igual que pasará en el CI;
   - `make up` levanta todo y el punto de salud responde.

Commits separados por bloque lógico (skill `commits`): `feat(<service>): add service skeleton`, `build(<service>): add docker setup`, `docs(architecture): add <service> component`.
