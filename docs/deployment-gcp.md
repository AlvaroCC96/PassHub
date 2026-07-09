# Deployment — Google Cloud Platform

Guía completa para desplegar PassHub en GCP usando Cloud Run, Cloud SQL, Cloud Storage y Secret Manager.

> **Proyecto personal** — un único ambiente productivo. Sin Kubernetes, sin Load Balancer, sin CDN.

---

## Arquitectura

```
Browser / NFC Card
      │
      ▼
┌─────────────────┐     ┌────────────────────┐
│  Cloud Run      │     │  Cloud Run         │
│  passhub-web    │────▶│  passhub-api       │
│  (Nginx + React)│     │  (FastAPI/Uvicorn) │
└─────────────────┘     └────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
       Cloud SQL           Cloud Storage       Secret Manager
       (PostgreSQL)        (Documentos)        (Secrets)
```

---

## Paso 1 — Requisitos previos

```bash
# Instalar Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Autenticarse
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev

# Variables globales (ajusta según tu proyecto)
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1
```

---

## Paso 2 — Crear proyecto GCP y habilitar APIs

```bash
# Crear proyecto (si no existe)
gcloud projects create ${PROJECT_ID} --name="PassHub"

# Seleccionar proyecto
gcloud config set project ${PROJECT_ID}

# Habilitar APIs necesarias
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com
```

---

## Paso 3 — Artifact Registry

```bash
# Crear repositorio Docker
gcloud artifacts repositories create passhub \
  --repository-format=docker \
  --location=${REGION} \
  --description="PassHub Docker images"

# Verificar
gcloud artifacts repositories list --location=${REGION}
```

---

## Paso 4 — Cloud SQL (PostgreSQL)

```bash
# Crear instancia (db-f1-micro es el tier más pequeño — suficiente para uso personal)
gcloud sql instances create passhub-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=${REGION} \
  --storage-type=SSD \
  --storage-size=10GB \
  --backup-start-time=03:00 \
  --no-assign-ip \
  --network=default

# Crear base de datos
gcloud sql databases create passhub --instance=passhub-db

# Crear usuario
gcloud sql users create passhub \
  --instance=passhub-db \
  --password=YOUR_STRONG_PASSWORD

# Obtener IP privada (para la variable POSTGRES_HOST)
gcloud sql instances describe passhub-db --format="value(ipAddresses[0].ipAddress)"
```

> **Nota sobre conectividad:** Cloud Run se conecta a Cloud SQL via IP privada (VPC) o via Cloud SQL Auth Proxy. La forma más simple para un proyecto personal es usar el **Cloud SQL Auth Proxy** como sidecar, pero para simplicidad usamos IP privada directa configurando el VPC Connector.

```bash
# Crear VPC Connector para que Cloud Run acceda a Cloud SQL via IP privada
gcloud compute networks vpc-access connectors create passhub-connector \
  --network=default \
  --region=${REGION} \
  --range=10.8.0.0/28
```

---

## Paso 5 — Cloud Storage (Documentos)

```bash
# Crear bucket privado (los documentos nunca son públicos — se sirven via signed URLs)
gcloud storage buckets create gs://passhub-documents-${PROJECT_ID} \
  --location=${REGION} \
  --uniform-bucket-level-access \
  --no-public-access-prevention

# Guardar el nombre del bucket
export GCS_BUCKET=passhub-documents-${PROJECT_ID}
```

---

## Paso 6 — Service Account para Cloud Run

```bash
# Crear service account dedicado (no usar la default Compute SA)
gcloud iam service-accounts create passhub-api-sa \
  --display-name="PassHub API Service Account"

export SA_EMAIL="passhub-api-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Permisos en Cloud Storage
gcloud storage buckets add-iam-policy-binding gs://${GCS_BUCKET} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.objectAdmin"

# Permisos para generar signed URLs (V4) — el SA necesita poder firmarse a sí mismo
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountTokenCreator"

# Permisos de Secret Manager
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"

# Permisos de Cloud SQL (si usas IP privada, no es necesario; si usas proxy sí)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client"
```

---

## Paso 7 — Secret Manager

Crear un secreto por variable sensible:

```bash
# Helper: crear o actualizar un secreto
create_secret() {
  local name=$1; local value=$2
  echo -n "${value}" | gcloud secrets create "${name}" \
    --data-file=- --replication-policy=automatic 2>/dev/null || \
  echo -n "${value}" | gcloud secrets versions add "${name}" --data-file=-
}

# Base de datos
create_secret passhub-db-host "IP_PRIVADA_CLOUD_SQL"
create_secret passhub-db-user "passhub"
create_secret passhub-db-password "YOUR_STRONG_PASSWORD"
create_secret passhub-db-name "passhub"

# JWT
create_secret passhub-jwt-secret "$(openssl rand -hex 64)"

# Google OAuth (obtener en https://console.cloud.google.com/apis/credentials)
create_secret passhub-google-client-id "YOUR_GOOGLE_CLIENT_ID"
create_secret passhub-google-client-secret "YOUR_GOOGLE_CLIENT_SECRET"

# OpenAI
create_secret passhub-openai-api-key "sk-..."
```

---

## Paso 8 — Build y push de imágenes

```bash
# Primero obtén la URL del backend (necesaria para el frontend)
# Si ya desplegaste antes: 
API_URL=$(gcloud run services describe passhub-api --region=${REGION} --format='value(status.url)')
# Si es la primera vez: usa un placeholder y redespliega el frontend después

export VITE_API_BASE_URL="${API_URL}/api/v1"

# Autenticar Docker con Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build y push
./scripts/build-api.sh
./scripts/build-web.sh
```

---

## Paso 9 — Deploy del backend (passhub-api)

Primero obtén la IP privada de Cloud SQL:

```bash
DB_HOST=$(gcloud sql instances describe passhub-db \
  --format="value(ipAddresses[0].ipAddress)")
```

Luego actualiza el secreto `passhub-db-host` con esa IP y despliega:

```bash
# Variables de entorno NO secretas (van inline)
# Los secretos se inyectan desde Secret Manager

gcloud run deploy passhub-api \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/passhub/passhub-api:latest" \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=0 \
  --max-instances=10 \
  --cpu=1 \
  --memory=1Gi \
  --service-account="${SA_EMAIL}" \
  --vpc-connector=passhub-connector \
  --vpc-egress=private-ranges-only \
  --set-env-vars="\
ENVIRONMENT=production,\
DEBUG=false,\
LOG_JSON=true,\
POSTGRES_PORT=5432,\
POSTGRES_DB=passhub,\
STORAGE_PROVIDER=gcs,\
STORAGE_GCS_PROJECT_ID=${PROJECT_ID},\
STORAGE_GCS_BUCKET=${GCS_BUCKET},\
STORAGE_BUCKET=${GCS_BUCKET},\
PUBLIC_SESSION_DURATION_MINUTES=10,\
PUBLIC_SIGNED_URL_DURATION_MINUTES=5,\
PUBLIC_MAX_FAILED_ATTEMPTS=5,\
PUBLIC_LOCKOUT_MINUTES=15" \
  --set-secrets="\
POSTGRES_HOST=passhub-db-host:latest,\
POSTGRES_USER=passhub-db-user:latest,\
POSTGRES_PASSWORD=passhub-db-password:latest,\
SECURITY_JWT_SECRET=passhub-jwt-secret:latest,\
SECURITY_GOOGLE_OAUTH_CLIENT_ID=passhub-google-client-id:latest,\
SECURITY_GOOGLE_OAUTH_CLIENT_SECRET=passhub-google-client-secret:latest,\
OPENAI_API_KEY=passhub-openai-api-key:latest" \
  --project=${PROJECT_ID}

# Obtener URL del backend
API_URL=$(gcloud run services describe passhub-api \
  --region=${REGION} \
  --format='value(status.url)' \
  --project=${PROJECT_ID})
echo "Backend URL: ${API_URL}"
```

---

## Paso 10 — Configurar variables dependientes de la URL del backend

Una vez tienes `API_URL`, actualiza los siguientes secretos/vars:

```bash
# CORS: solo el frontend puede hacer requests al backend
gcloud run services update passhub-api \
  --region=${REGION} \
  --update-env-vars="CORS_ORIGINS=[\"https://passhub-web-XXXXX.run.app\"]" \
  --project=${PROJECT_ID}

# Google OAuth redirect URI
gcloud run services update passhub-api \
  --region=${REGION} \
  --update-env-vars="SECURITY_GOOGLE_OAUTH_REDIRECT_URI=${API_URL}/api/v1/auth/callback" \
  --project=${PROJECT_ID}

# Public portal base URL
gcloud run services update passhub-api \
  --region=${REGION} \
  --update-env-vars="PUBLIC_PORTAL_BASE_URL=https://passhub-web-XXXXX.run.app,FRONTEND_URL=https://passhub-web-XXXXX.run.app" \
  --project=${PROJECT_ID}
```

---

## Paso 11 — Deploy del frontend (passhub-web)

```bash
# Rebuil con la URL real del backend
export VITE_API_BASE_URL="${API_URL}/api/v1"
./scripts/build-web.sh

# Deploy
gcloud run deploy passhub-web \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/passhub/passhub-web:latest" \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=0 \
  --max-instances=5 \
  --cpu=1 \
  --memory=512Mi \
  --project=${PROJECT_ID}

WEB_URL=$(gcloud run services describe passhub-web \
  --region=${REGION} \
  --format='value(status.url)' \
  --project=${PROJECT_ID})
echo "Frontend URL: ${WEB_URL}"
```

---

## Paso 12 — Migraciones Alembic (Cloud SQL)

Las migraciones se corren manualmente desde tu máquina local usando el **Cloud SQL Auth Proxy**.

```bash
# Terminal 1: iniciar el proxy
cloud-sql-proxy ${PROJECT_ID}:${REGION}:passhub-db --port 5433

# Terminal 2: correr migraciones
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5433
export POSTGRES_USER=passhub
export POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
export POSTGRES_DB=passhub
./scripts/migrate.sh
```

---

## Paso 13 — Configurar Google OAuth

En [Google Cloud Console → APIs → Credentials](https://console.cloud.google.com/apis/credentials):

1. Abre tu OAuth 2.0 Client ID
2. En **Authorized redirect URIs** agrega:
   ```
   https://passhub-api-XXXXX.run.app/api/v1/auth/callback
   ```
3. En **Authorized JavaScript origins** agrega:
   ```
   https://passhub-web-XXXXX.run.app
   ```
4. Guarda cambios

---

## Paso 14 — Health checks

```bash
# Verificar que el backend responde
curl https://passhub-api-XXXXX.run.app/api/v1/health
# Esperado: {"status": "ok", "service": "PassHub API", "environment": "production"}

curl https://passhub-api-XXXXX.run.app/api/v1/health/liveness
# Esperado: {"status": "alive"}

curl https://passhub-api-XXXXX.run.app/api/v1/health/readiness
# Esperado: {"status": "ready", "database": "ok"}
```

---

## Smoke Test Checklist

| # | Prueba | Pasos |
|---|--------|-------|
| 1 | Frontend carga | Abrir `https://passhub-web-XXXXX.run.app` |
| 2 | Login Google | Hacer login con Google |
| 3 | Dashboard carga | Navegar al dashboard |
| 4 | DrivePass carga | Ir a DrivePass |
| 5 | Crear vehículo | Crear un vehículo de prueba |
| 6 | Subir documento | Subir un PDF al vehículo |
| 7 | Ver documento | Abrir el documento (signed URL) |
| 8 | IA funciona | Usar extracción AI en un documento |
| 9 | Activar acceso público | En detalle del vehículo → Acceso Público → Crear PIN |
| 10 | Copiar link público | Copiar el link generado |
| 11 | Abrir link en celular | Pegar el link en el celular |
| 12 | Ingresar PIN | Ingresar el PIN desde el celular |
| 13 | Ver documentos públicos | Verificar que los docs marcados como públicos aparecen |
| 14 | Ver documento público | Hacer click en "Ver" → debe abrirse (signed URL) |
| 15 | Cerrar sesión pública | Click en "Cerrar sesión" |

---

## Monitoring básico (recomendado)

Crear alertas en Cloud Monitoring:

```bash
# Errores 5xx en Cloud Run API (más de 5 en 5 minutos)
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL \
  --display-name="PassHub API 5xx errors" \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"' \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

O más simple: en Cloud Console → Monitoring → Alerting → Create Policy, configurar manualmente:

- **API 5xx rate**: `run.googleapis.com/request_count` con `response_code_class=5xx` > 5 en 5min
- **API latencia alta**: `run.googleapis.com/request_latencies` p99 > 5s
- **Cloud SQL CPU**: `cloudsql.googleapis.com/database/cpu/utilization` > 80%
- **Cloud SQL storage**: `cloudsql.googleapis.com/database/disk/utilization` > 80%

---

## Redeploy rápido (después del primer deploy)

```bash
export PROJECT_ID=your-project
export REGION=us-central1

# Solo backend
TAG=$(date +%Y%m%d-%H%M%S) ./scripts/build-api.sh && ./scripts/deploy-api.sh

# Solo frontend (si cambia la URL del backend, rebuildearlo primero)
export VITE_API_BASE_URL=https://passhub-api-XXXXX.run.app/api/v1
TAG=$(date +%Y%m%d-%H%M%S) ./scripts/build-web.sh && ./scripts/deploy-web.sh
```

---

## Notas sobre cookies y CORS

El frontend y backend están en dominios distintos de Cloud Run (`*.run.app`). Esto afecta las cookies HttpOnly:

- `SameSite=None; Secure` — necesario para cookies cross-origin
- `CORS_ORIGINS` debe incluir la URL exacta del frontend (sin barra final)
- `credentials: "include"` ya está configurado en el frontend (`api-client.ts`)

El backend configura las cookies correctamente cuando `ENVIRONMENT=production` (`is_production=True`), lo que activa `Secure=True` en las cookies de sesión.

**Limitación actual:** las URLs de Cloud Run son largas y cambian si se recrea el servicio. Para uso con NFC, se recomienda configurar un dominio personalizado en un sprint futuro (5 minutos de trabajo una vez que tienes el dominio).

---

## Variables de referencia rápida

| Variable | Dónde se configura | Ejemplo |
|----------|-------------------|---------|
| `POSTGRES_HOST` | Secret Manager | `10.x.x.x` (IP privada Cloud SQL) |
| `POSTGRES_PASSWORD` | Secret Manager | _(generado)_ |
| `SECURITY_JWT_SECRET` | Secret Manager | `openssl rand -hex 64` |
| `SECURITY_GOOGLE_OAUTH_CLIENT_ID` | Secret Manager | `xxx.apps.googleusercontent.com` |
| `SECURITY_GOOGLE_OAUTH_CLIENT_SECRET` | Secret Manager | `GOCSPX-xxx` |
| `OPENAI_API_KEY` | Secret Manager | `sk-xxx` |
| `STORAGE_PROVIDER` | Cloud Run env var | `gcs` |
| `STORAGE_GCS_BUCKET` | Cloud Run env var | `passhub-documents-xxx` |
| `CORS_ORIGINS` | Cloud Run env var | `["https://passhub-web-xxx.run.app"]` |
| `PUBLIC_PORTAL_BASE_URL` | Cloud Run env var | `https://passhub-web-xxx.run.app` |
| `VITE_API_BASE_URL` | Docker build arg | `https://passhub-api-xxx.run.app/api/v1` |
