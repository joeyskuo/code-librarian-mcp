import base64
import logging

from config import settings

logger = logging.getLogger(__name__)


def setup_telemetry() -> None:
    public_key = settings.langfuse_public_key
    secret_key = settings.langfuse_secret_key
    base_url = settings.langfuse_base_url

    if not all([public_key, secret_key, base_url]):
        logger.info("Langfuse env vars not set. Telemetry inactive")
        return

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
    exporter = OTLPSpanExporter(
        endpoint=f"{base_url}/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {auth}"},
    )
    provider = TracerProvider(resource=Resource({"service.name": "code-librarian-mcp"}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logger.info("Telemetry configured: exporting traces to %s", base_url)
