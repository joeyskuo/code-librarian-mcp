import base64
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# OTEL must be configured before importing FastMCP
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

_auth = base64.b64encode(
    f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
).decode()

_exporter = OTLPSpanExporter(
    endpoint=f"{os.environ['LANGFUSE_BASE_URL']}/api/public/otel/v1/traces",
    headers={"Authorization": f"Basic {_auth}"},
)

_provider = TracerProvider(resource=Resource({"service.name": "code-librarian-mcp"}))
_provider.add_span_processor(BatchSpanProcessor(_exporter))
trace.set_tracer_provider(_provider)

from server import mcp

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8001))
    mcp.run(transport="streamable-http", host=host, port=port)
