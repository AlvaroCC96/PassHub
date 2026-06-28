from fastapi import FastAPI

from src.core.config import Settings


def configure_tracing(app: FastAPI, settings: Settings) -> None:
    """Wires OpenTelemetry instrumentation when `OTEL_ENABLED=true`.

    No exporter is attached and no metrics are sent in Sprint 0 — this only
    keeps the integration point ready so enabling tracing later is a config
    change, not a code change.
    """
    if not settings.observability.enabled:
        return

    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider

    resource = Resource.create({SERVICE_NAME: settings.observability.service_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))
