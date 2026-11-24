# Spec Delta

## Purpose

Que solo las personas autenticadas accedan a la API y cada una vea solo sus clases. El emisor de identidad real de CoTeach está pendiente; mientras, un emisor de pruebas aislado firma los tokens de la demo ([ADR-0004](../../../../../docs/ADR/0004-access-and-retention.md)). El contrato está en [CONTRACTS](../../../../../docs/CONTRACTS/README.md).

## ADDED Requirements

### Requirement: Autenticación con token
Toda petición a `/v1` SHALL llevar un token firmado por el emisor configurado y sin caducar; si no, la API la rechaza con 401 y no devuelve datos de ninguna clase (RNF-01).

#### Scenario: Sin token
- **WHEN** una petición a `/v1` no lleva token
- **THEN** recibe 401 con el código `unauthenticated`.

#### Scenario: Token caducado o mal firmado
- **WHEN** una petición lleva un token caducado o firmado con otra clave
- **THEN** recibe 401 sin datos de la clase solicitada.

### Requirement: Acceso limitado a las clases de cada persona
La API SHALL resolver en el servidor a qué clases puede acceder cada persona, a partir del sujeto y el rol del token y de los participantes de la clase, y SHALL responder 404 ante una clase ajena para no revelar su existencia. El rol nunca se toma del cuerpo de la petición (RNF-01).

#### Scenario: Docente de la clase
- **WHEN** la docente que envió una clase consulta su trabajo
- **THEN** recibe su estado.

#### Scenario: Persona ajena a la clase
- **WHEN** una persona autenticada que no participa en la clase consulta su trabajo o su resultado
- **THEN** recibe 404 `resource_not_available`, sin contenido ni metadatos de esa clase.

#### Scenario: Alumno ante un resultado sin publicar
- **WHEN** un alumno participante consulta el resultado de una clase que no está publicada
- **THEN** recibe 404 y no ve la transcripción ni el análisis.

#### Scenario: Rol declarado en el cuerpo
- **WHEN** un alumno envía una petición con un rol docente en el cuerpo
- **THEN** la API aplica el rol de su token y no le concede permisos de docente.

### Requirement: Emisor de pruebas aislado
El emisor de tokens de pruebas SHALL existir solo cuando está activado de forma explícita por configuración y SHALL emitir tokens únicamente para los usuarios sintéticos configurados (RNF-01).

#### Scenario: Emisor desactivado
- **WHEN** el emisor de pruebas no está activado y alguien solicita un token
- **THEN** la ruta no existe y responde 404.

#### Scenario: Usuario no configurado
- **WHEN** con el emisor activado se solicita un token para un usuario que no está entre los sintéticos
- **THEN** no se emite ningún token.
