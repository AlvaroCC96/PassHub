# Public Access — Secure Vehicle Portal

## Qué es Public Access

Public Access es la funcionalidad que permite a un usuario de PassHub compartir sus documentos vehiculares con un tercero (mecánico, inspector, carabinero) **sin requerir que el tercero tenga una cuenta en la plataforma**.

El propietario genera un **Public Token** para uno de sus vehículos y comparte el enlace:

```
https://passhub.app/p/F7mKs92PwQeLmA9QWx3LdZ
```

El tercero accede con ese enlace, ingresa el **PIN de 4 dígitos** que el propietario le comunicó, y obtiene una **Public Session** de 10 minutos para ver los documentos del vehículo.

## Qué es el Public Token

El Public Token es un identificador aleatorio de **22 caracteres Base62** (`[a-zA-Z0-9]`) que identifica el acceso público de un vehículo. Es:

- **Completamente aleatorio** — generado con `secrets.choice` (CSPRNG del OS), ~131 bits de entropía.
- **Sin información** — no contiene el ID del vehículo ni ningún timestamp.
- **Único e irrecuperable** — si el propietario regenera el token, el anterior deja de funcionar inmediatamente y todos los Public Sessions activos quedan revocados.
- **URL-safe** — usa solo letras y dígitos, sin caracteres especiales.

Ejemplo: `F7mKs92PwQeLmA9QWx3LdZ`

Este token es el identificador que **viajará escrito dentro de la tarjeta NFC en Sprint 5**, reemplazando el enlace manual. La URL del portal público es simplemente `https://passhub.app/p/{public_token}`.

## Qué es VehiclePublicAccess

`VehiclePublicAccess` es la entidad que representa la configuración del acceso público de un vehículo. Existe una sola por vehículo (soft-delete, nunca se eliminan filas).

| Campo | Descripción |
|---|---|
| `public_token` | Token Base62 de 22 chars que aparece en la URL |
| `pin_hash` | Hash Argon2id del PIN de 4 dígitos (nunca el PIN) |
| `enabled` | `false` → acceso desactivado (403) |
| `failed_attempts` | Intentos fallidos de PIN consecutivos |
| `locked_until` | Si está seteado y en el futuro → acceso bloqueado temporalmente |
| `last_access_at` | Último intento (correcto o incorrecto) |
| `last_success_at` | Último acceso exitoso |

### Estado del acceso (`PublicAccessStatus`)

El estado se calcula en el dominio, no se persiste en columna:

| Estado | Condición |
|---|---|
| `LOCKED` | `locked_until` existe y está en el futuro |
| `DISABLED` | `enabled = false` |
| `ACTIVE` | ninguna de las anteriores |

## Qué es Public Session

`PublicSession` es un token de sesión de corta duración (10 minutos) emitido después de una verificación exitosa del PIN. Se implementa con un **token opaco random**, no JWT.

| Campo | Descripción |
|---|---|
| `session_token_hash` | SHA-256 del token raw (nunca el token en claro) |
| `expires_at` | `created_at + 10 minutos` |
| `ip_address` | IP del cliente (para auditoría) |
| `user_agent` | User-Agent del cliente (para auditoría) |
| `revoked_at` | Si está seteado → sesión inválida |

El **token raw** se entrega al cliente una sola vez en la respuesta de autenticación. Solo el hash SHA-256 queda en la base de datos. En cada request posterior el cliente envía el token raw y el servidor verifica contra el hash.

### Estado de la sesión (`SessionStatus`)

| Estado | Condición |
|---|---|
| `REVOKED` | `revoked_at IS NOT NULL` |
| `EXPIRED` | `expires_at <= NOW()` |
| `ACTIVE` | ninguna de las anteriores |

## Relación con NFC (Sprint 5)

En Sprint 5, el `public_token` se escribirá dentro de una tarjeta NFC en formato NDEF URI record:

```
https://passhub.app/p/{public_token}
```

Cuando alguien acerca su teléfono a la tarjeta NFC adherida al vehículo (parabrisas, guantera), el sistema operativo abre esa URL automáticamente en el navegador. El flujo sigue siendo idéntico al del enlace manual:

1. Teléfono lee la tarjeta → abre `https://passhub.app/p/F7mKs92PwQeLmA9QWx3LdZ`
2. Portal público solicita PIN
3. PIN correcto → Public Session de 10 minutos
4. Documentos visibles

La arquitectura de Public Access fue diseñada desde el inicio pensando en este flujo: el `public_token` es el identificador canónico que viaja en la tarjeta.

## Arquitectura

```
modules/
  public_access/
    domain/
      entities/        VehiclePublicAccess, PublicSession
      value_objects/   PublicAccessStatus, SessionStatus
      events.py        constantes de auditoría (no despachados aún)
    application/
      ports/           PublicAccessRepository, PublicSessionRepository (Protocols)
      services/        PublicAccessService, PublicSessionService
    infrastructure/
      models.py        VehiclePublicAccessModel, PublicSessionModel
      repositories.py  SqlAlchemyPublicAccessRepository, SqlAlchemyPublicSessionRepository
      token_generator.py  PublicTokenGenerator (Base62, CSPRNG)
      pin_hasher.py       PinHasher (Argon2id)
```

`public_access` es un **módulo top-level**, hermano de `identity`, `platform`, `drivepass` e `intelligence`. No importa de `drivepass` en ninguna capa. El campo `vehicle_id` en `vehicle_public_access` es un UUID plano sin FK de base de datos (el mismo patrón que usa `intelligence` para `document_id`/`vehicle_id`).

## PIN

- **4 dígitos numéricos** (e.g., `1234`).
- Nunca se almacena el PIN en claro.
- Se almacena únicamente el hash Argon2id (`PinHasher.hash_pin`).
- Nunca se devuelve el PIN ni el hash en ninguna respuesta de API.
- Nunca se loggea el PIN.
- `PinHasher.verify_pin(pin_hash=..., pin=...)` compara PIN ingresado contra hash almacenado.

## Seguridad

- El `public_token` tiene ~131 bits de entropía — adivinar uno por fuerza bruta es computacionalmente inviable.
- El PIN de 4 dígitos solo tiene 10,000 valores posibles. La protección contra fuerza bruta se implementa con **Rate Limit + Lockout** en Parte 2 (`failed_attempts`, `locked_until`).
- El session token se hashea con SHA-256 antes de persistir. Si la DB se filtra, los tokens no sirven sin el raw value que solo tiene el cliente.
- La sesión dura 10 minutos — ventana corta para minimizar el impacto de un token comprometido.
- Regenerar el `public_token` revoca todas las sesiones activas inmediatamente.

## Tablas

### `vehicle_public_access`

```sql
id                UUID PK
vehicle_id        UUID UNIQUE      -- sin FK (módulo desacoplado)
public_token      VARCHAR(64) UNIQUE
pin_hash          TEXT
enabled           BOOLEAN
failed_attempts   INTEGER
locked_until      TIMESTAMPTZ NULL
last_access_at    TIMESTAMPTZ NULL
last_success_at   TIMESTAMPTZ NULL
created_at        TIMESTAMPTZ
updated_at        TIMESTAMPTZ
deleted_at        TIMESTAMPTZ NULL
```

### `public_sessions`

```sql
id                          UUID PK
vehicle_public_access_id    UUID       -- sin FK (módulo desacoplado)
session_token_hash          TEXT
expires_at                  TIMESTAMPTZ
ip_address                  VARCHAR(45) NULL
user_agent                  TEXT NULL
revoked_at                  TIMESTAMPTZ NULL
created_at                  TIMESTAMPTZ
updated_at                  TIMESTAMPTZ
```

## Eventos de auditoría (preparados, no despachados aún)

```python
PUBLIC_ACCESS_CREATED
PUBLIC_ACCESS_ENABLED
PUBLIC_ACCESS_DISABLED
PUBLIC_TOKEN_REGENERATED
PUBLIC_PIN_CHANGED
PUBLIC_SESSION_CREATED
PUBLIC_SESSION_REVOKED
```

Se despacharán con `category="public_access.audit"` en el mismo patrón structlog del resto de los módulos, cuando se implementen los endpoints en Parte 2.

## Endpoints (Parte 2)

Los endpoints REST serán implementados en Sprint 4.5 Parte 2. No existen aún.
