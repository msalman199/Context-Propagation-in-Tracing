from flask import Flask, request, jsonify
import logging
import random
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

resource = Resource.create({"service.name": "inventory-service", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/inventory/order/<order_id>')
def check_inventory(order_id):
    context = extract(request.headers)
    with tracer.start_as_current_span("check_inventory", context=context) as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("service.name", "inventory-service")
        logger.info(f"Checking inventory for order: {order_id}")

        with tracer.start_as_current_span("database_lookup") as db_span:
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "inventory")
            lookup_time = random.uniform(0.05, 0.2)
            time.sleep(lookup_time)
            db_span.set_attribute("db.duration_ms", lookup_time * 1000)

        available = random.choice([True, True, True, False])
        quantity = random.randint(1, 100) if available else 0

        span.set_attribute("inventory.available", available)
        span.set_attribute("inventory.quantity", quantity)
        if not available:
            span.add_event("Inventory out of stock", {"order.id": order_id})

        result = {
            "order_id": order_id,
            "available": available,
            "quantity": quantity,
            "warehouse": f"warehouse_{random.randint(1, 3)}"
        }
        return jsonify(result)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "inventory-service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
