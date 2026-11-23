# Preguntas para Lay — CoTeach

Respuestas facilitadas por Lay. Se conserva el contenido de las respuestas y se organiza por temas para consulta durante la definición del PRD.

## 1. Plataforma e integración

### 1. ¿Tenéis servidor? ¿Qué ha ocurrido con la web desarrollada en Lovable? ¿Sigue siendo la plataforma definitiva? ¿Nosotras no hosteamos? ¿Mantenemos el producto en local o qué os parecería Groq?

**Lay:** Tenemos un servidor -en realidad, es uno mío que he cedido temporalmente- con un Odoo corriendo; además, usamos los servicios de Nextcloud que ofrece https://nuberu.org/.

La web de Lovable está out; había quedado desfasada y queremos hacer algo más chulo, ya con imagen propia.

Sobre local/proveedores, lo podemos tratar en la reunión del jueves.

### 2. ¿La aplicación que desarrollemos debe integrarse en CoTeach o puede funcionar como servicio independiente? ¿Podemos ver la interfaz de CoTeach? Planteamos la opción de crear también un Streamlit sencillo para poder presentar el proyecto de forma visual los días 11 y 15 de diciembre.

**Lay:** Debería ser un servicio independiente, el cual lo integraríamos mediante API con CoTeach. Actualmente sólo hay un prototipo para validar el stack y algunos mockups. Adelante con Streamlit :-)

### 3. ¿Tenéis ya un backend, una base de datos y un sistema de autenticación de usuarios? ¿Tenemos acceso al MVP?

**Lay:** Sí; usaremos Odoo como backend, que utiliza PostgreSQL como base de datos relacional. Este backend se encargará de todo el trabajo administrativo, de la gestión de usuarios, reservas y pagos, de la creación de tokens de vida corta para las salas de videollamadas...

### 4. ¿Podemos acceder al código o a la documentación técnica de la plataforma?

**Lay:** Os pasaré los documentos técnicos; no obstante, tened en cuenta lo comentado: es un borrador de un MVP, que ha sido validado a nivel técnico pero no es ni definitivo, ni 100% funcional.

## 2. Infraestructura y costes

### 5. ¿Disponéis de servidores propios o de algún servicio de alojamiento contratado?

**Lay:** Contestada en 1A.

### 6. ¿Tienen acceso a GPU para ejecutar modelos de IA?

**Lay:** A nivel local, pero podemos estudiar utilizar servicios remotos de GPU para correr modelos de forma privada.

### 7. ¿Cuántas clases grabadas esperan procesar aproximadamente al día?

**Lay:** Para una primera fase, podemos estimar unas 10. El servicio debe ser escalable por diseño para poder asumir mayores cargas de trabajo en el futuro.

## 3. Grabaciones y transcripción

### 8. ¿Las clases se grabarán directamente desde CoTeach o se subirán archivos de audio previamente grabados?

**Lay:** Se grabarán usando la funcionalidad del servicio de videollamadas (BigBlueButton), pero toda la app está diseñada para ser agnóstica y estar desacoplada del resto del stack: para lo que afecta a este desarrollo, podemos asumir que recibirá un archivo de audio -comprimido- mediante API.

### 9. ¿Qué duración suelen tener las clases y cuántos participantes pueden intervenir?

**Lay:** De '30 a 60'. Hay dos modalidades: 1-1 (individuales) o 1-4 (grupales).

### 10. ¿Qué idiomas deben soportarse inicialmente?

**Lay:** Castellano, catalán, inglés, francés, chino... estaría bien. Si supone una limitación (no debería, el más raro es el catalán y hay modelos específicos para este idioma), podemos prescindir de idiomas en esta fase.

### 11. ¿Existen grabaciones de prueba autorizadas, con ejemplos de los resultados que esperáis obtener? Si no, planteamos grabar audios o descargar contenido por nuestra cuenta de internet.

**Lay:** Hay unas pocas, 3 de momento. Yo utilizaría una mezcla de grabaciones reales con otras simuladas (grabadas por nosotras) y con ejemplos conversacionales obtenidos de internet.

### 12. ¿Necesitáis la transcripción en tiempo real o es suficiente procesarla después de terminar la clase?

**Lay:** No, no es necesaria a tiempo real.

## 4. Identificación de participantes

### 13. ¿Profesorado y alumnado tendrán cuentas individuales dentro de CoTeach?

**Lay:** Sí.

### 14. ¿Es suficiente distinguir a las personas hablantes y permitir asignarles nombres o nicknames manualmente?

**Lay:** Sí; idealmente, se asignarían los nombres de forma programática. Mediante API se recibiría el archivo de audio más el número de participantes y los nombres.

### 15. ¿Necesitáis identificar automáticamente al mismo profesor o alumno entre diferentes sesiones?

**Lay:** Esta lógica podría pertenecer a otra iteración, no es necesario que la resolvamos ahora (a no ser que podamos y sepamos! ;-))

## 5. Análisis pedagógico

### 16. ¿El análisis debe ser individual para cada alumno o puede ser un resumen general de la clase?

**Lay:** En el caso de las clases individuales, no hay duda. En el caso de las grupales, sería ideal tener resúmenes individualizados.

### 17. ¿El profesor podrá revisar y corregir los resultados generados por la IA antes de compartirlos?

**Lay:** ¡Sí! Aunque no debería ser un motivo de bloqueo: si pasadas X horas, la profesora no ha revisado la transcripción, pasaría automáticamente.

### 18. ¿Queréis que cada resultado esté vinculado al minuto exacto de la grabación?

**Lay:** Sería muy interesante, sí, no necesariamente para cada resultado, pero sí poder hacerlo para casos donde sea realmente útil (pronunciación, frases concretas...)

## 6. Privacidad y seguridad

### 19. ¿Disponéis de una política de privacidad y protección de datos específica para CoTeach?

**Lay:** Aún no.

### 20. ¿Dónde queréis almacenar las grabaciones y transcripciones?

**Lay:** En nuestro propio servidor, con un sistema de purga de las grabaciones tras X días.

### 21. ¿Quién podrá acceder a ellas: profesorado, alumnado, administradores?

**Lay:** Profes y alumnado.

### 22. ¿Durante cuánto tiempo deben conservarse las grabaciones? ¿Se podrán eliminar automáticamente?

**Lay:** Pongamos dos semanas de conservación del audio original.

### 23. ¿Está previsto que participen menores de edad?

**Lay:** Sí, aunque no en esta fase.

## 7. Entrega y continuidad

### 24. ¿Quién mantendrá y desplegará la solución cuando termine el bootcamp?

**Lay:** Nosotras :-)

### 25. ¿Hay alguna tecnología, proveedor o restricción técnica que debamos respetar?

**Lay:** Sofware libre como requisito. Implementar la privacidad por diseño allá donde sea menester. Priorizar soluciones que sean soberanas tecnológicamente y que integren en su producto el impacto ecológico.

## Preguntas sin respuesta documentada en este intercambio

- Presupuesto disponible para infraestructura o servicios externos.
- Qué funcionalidades son imprescindibles para la presentación del 15 de diciembre.
- Plazo exacto de revisión del profesorado antes de compartir automáticamente los resultados.
