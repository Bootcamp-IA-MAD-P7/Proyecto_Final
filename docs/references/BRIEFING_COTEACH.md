# Propuesta de proyecto final 

**CoTeach | Transcripción, diarización y análisis pedagógico inteligente de clases**

## 1. Sobre CoTeach

[CoTeach](https://coteach.lovable.app/) es un proyecto de cooperativa de plataforma digital en proceso de constitución, acompañado por **Coòpolis**, el Ateneu Cooperatiu de Barcelona.

Nuestro objetivo es desarrollar una alternativa cooperativa, ética y de código abierto a las plataformas tradicionales de clases particulares de idiomas, situando a docentes y estudiantes en el centro del modelo.

Apostamos por una plataforma en la que el profesorado participe en la propiedad y gobernanza, tenga control sobre sus datos y condiciones de trabajo y pueda beneficiarse directamente del valor que genera. El proyecto presta también especial atención a la diversidad lingüística, las lenguas minorizadas y la accesibilidad a la enseñanza de idiomas.

**CoTeach ha sido [finalista de la convocatoria 4D](https://4d.cat/es/convocatoria/) – Derechos Digitales desde el Diseño**, una iniciativa que promueve tecnologías comprometidas con la digitalización democrática, los derechos digitales y la soberanía tecnológica.

En el ámbito tecnológico, apostamos por el **software libre, los estándares abiertos, la privacidad y el uso responsable de la inteligencia artificial**. Queremos incorporar la IA como una herramienta al servicio del profesorado y del alumnado, no como un sustituto de la labor docente.

## 2. Objetivo del proyecto

El proyecto consiste en desarrollar un **MVP open source capaz de procesar grabaciones de clases particulares**, tanto individuales (*one-to-one*) como grupales (*one-to-many*), y transformarlas en recursos estructurados que faciliten el repaso y refuercen el aprendizaje.

La propuesta parte de una necesidad real de CoTeach: aprovechar el contenido de las clases grabadas para que el alumnado pueda revisar no solo lo que se ha dicho, sino especialmente aquello que resulta relevante para su proceso de aprendizaje.

El sistema deberá generar dos resultados complementarios:

1. **Transcripción diarizada:** registro completo de la sesión, con identificación de los diferentes interlocutores, sus intervenciones y marcas temporales.
2. **Repaso pedagógico inteligente:** extracción y organización de los aprendizajes más relevantes de la clase, de manera que puedan consultarse posteriormente de forma estructurada y contextualizada.

El objetivo final es **convertir una clase grabada en un recurso de aprendizaje reutilizable y personalizado**, sin añadir carga de trabajo al profesorado.

## 3. Alcance técnico del proyecto

### Bloque 1. Transcripción y diarización

La idea inicial es utilizar **Whisper** como motor de reconocimiento de voz, incorporando una capa adicional de diarización para distinguir las intervenciones de los distintos participantes.

El trabajo incluiría:

- Procesamiento de archivos de audio procedentes de clases grabadas.
- Transcripción automática del contenido hablado.
- Diarización para identificar y separar las intervenciones de cada interlocutor.
- Incorporación de marcas temporales.
- Generación de una transcripción estructurada y consultable.

Se explorarán herramientas y modelos open source para implementar la diarización, prestando especial atención a escenarios con múltiples participantes, distintos idiomas y posibles solapamientos de voz.

La selección definitiva de tecnologías y la arquitectura del sistema formarán parte del trabajo de investigación y desarrollo del equipo.

### Bloque 2. Análisis pedagógico automatizado

A partir de la transcripción diarizada, se desarrollará una segunda capa de procesamiento que permita **identificar, clasificar y estructurar los contenidos pedagógicamente relevantes de cada sesión**.

Entre los elementos que se pretende identificar se encuentran:

- **Vocabulario:** palabras nuevas, expresiones y términos relevantes trabajados durante la clase.
- **Gramática y construcciones lingüísticas:** estructuras, reglas y patrones explicados o practicados.
- **Errores y correcciones:** errores detectados en las intervenciones del alumnado y sus correspondientes correcciones.
- **Aciertos reforzados:** usos correctos del idioma, avances y aprendizajes consolidados.
- **Explicaciones y conceptos clave:** contenidos especialmente relevantes para comprender o repasar la sesión.
- **Dudas resueltas:** preguntas del alumnado y explicaciones ofrecidas por el profesorado.

El resultado deberá organizarse en una estructura que facilite su visualización posterior en CoTeach, idealmente vinculando cada elemento con el fragmento de la transcripción del que procede.

**La estrategia concreta de análisis queda abierta a la investigación del alumnado.** 

Se podrán evaluar diferentes modelos de lenguaje (LLMs), técnicas de NLP, sistemas de extracción de información y mecanismos de generación de salidas estructuradas.

Se valorarán especialmente la calidad y trazabilidad de los resultados, la eficiencia computacional, la privacidad y la posibilidad de utilizar soluciones open source ejecutables en infraestructura propia.

## 4. Entregables esperados

El resultado del proyecto será un **MVP funcional, demostrable y preparado para evolucionar**, con los siguientes componentes:

1. **Motor de transcripción y diarización:** capaz de procesar una grabación y generar una transcripción estructurada con identificación de interlocutores y marcas temporales.
2. **Motor de análisis pedagógico:** capaz de procesar la transcripción para extraer y clasificar información relevante para el aprendizaje.
3. **Salida estructurada de resultados:** un formato que permita consultar tanto la transcripción completa como los elementos de repaso, facilitando su futura integración en la interfaz de CoTeach.
4. **API o mecanismo de integración:** que permita incorporar las funcionalidades desarrolladas a la plataforma.
5. **Código fuente y documentación técnica:** incluyendo arquitectura, tecnologías utilizadas, instrucciones de instalación, ejecución y pruebas.

Se priorizará la calidad y funcionalidad del flujo completo —desde la grabación hasta el material de repaso— frente a la implementación de numerosas funcionalidades adicionales.

## 5. Tecnologías y metodología de trabajo

El proyecto se desarrollará siguiendo principios de **software libre y open source**, priorizando tecnologías abiertas, interoperables y que eviten dependencias innecesarias de proveedores externos.

Como punto de partida se plantean las siguientes opciones:

| **Componente**        | **Propuesta inicial**                                |
| --------------------- | ---------------------------------------------------- |
| Reconocimiento de voz | Whisper                                              |
| Diarización           | Por investigar y seleccionar                         |
| Análisis pedagógico   | LLMs y técnicas NLP, por definir                     |
| Backend e integración | Por definir según la arquitectura                    |
| Repositorio de código | GitHub, GitLab, Forgejo, Gitea u otra forja acordada |
| Metodología           | Agile, con desarrollo iterativo e incremental        |



La metodología de trabajo será **Agile**, adaptada a la duración y características del bootcamp.



Se propone trabajar mediante un backlog de tareas priorizadas, iteraciones cortas, entregas incrementales y reuniones periódicas de seguimiento, demostración y feedback.

Las decisiones técnicas se tomarán progresivamente, a partir de la investigación, experimentación y evaluación de alternativas.

Asimismo, se tendrán en cuenta las implicaciones de privacidad y protección de datos, utilizando grabaciones consentidas o datos de prueba apropiados y evitando publicar información personal o sensible en los repositorios.

## 6. Organización y colaboración

La duración estimada es de **4-5 semanas**, adaptando el alcance a los recursos disponibles, la composición del equipo y los objetivos formativos del bootcamp.

CoTeach actuará como entidad colaboradora y cliente del proyecto, aportando:

- Contexto del problema y casos de uso reales.
- Requisitos funcionales y criterios de aceptación.
- Ejemplos de entrada y resultados esperados.
- Acompañamiento mediante reuniones semanales de seguimiento y feedback.
- Validación funcional de las entregas y participación en la presentación final.

Por su parte, el equipo de estudiantes asumirá la investigación tecnológica, propuesta de arquitectura, desarrollo, pruebas, documentación y presentación de resultados.

El proyecto se organizará de forma incremental, priorizando primero la obtención de una transcripción diarizada funcional y, posteriormente, el desarrollo y validación del análisis pedagógico.

## 7. Valor formativo y continuidad

El proyecto plantea un reto real de inteligencia artificial aplicada a la educación, que combina diferentes disciplinas y competencias:

- Procesamiento de audio y reconocimiento automático del habla.
- Diarización y procesamiento de conversaciones multipersona.
- Procesamiento del lenguaje natural y modelos LLM.
- Extracción, clasificación y estructuración de información.
- Diseño de APIs e integración de servicios de IA.
- Evaluación de modelos, documentación técnica y desarrollo colaborativo mediante metodología Agile.





Más allá del desafío técnico, el proyecto plantea una cuestión especialmente interesante: **cómo convertir una conversación educativa en conocimiento estructurado, contextualizado y útil para el aprendizaje**.

El resultado podrá evolucionar posteriormente dentro de CoTeach, incorporando mejoras, nuevos modelos, más idiomas y funcionalidades de aprendizaje personalizado.

Se trata, por tanto, de una oportunidad para trabajar sobre un caso de uso real, con impacto educativo y vinculado a un proyecto cooperativo que apuesta por la soberanía tecnológica, el software libre y una inteligencia artificial al servicio de las personas.
