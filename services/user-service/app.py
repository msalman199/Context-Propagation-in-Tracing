from flask import Flask, request, jsonify
import requests
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import inject
from opentelemetry.sdk.resources import Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

resource = Resource.create({"service.name": "user-service", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/user/<user_id>')
def get_user(user_id):
    with tracer.start_as_current_span("get_user_operation") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("service.name", "user-service")
        logger.info(f"Processing request for user: {user_id}")

        user_data = {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        }

        try:
            headers = {}
            inject(headers)
            logger.info(f"Calling order service with headers: {headers}")

            response = requests.get(
                f"http://localhost:5002/orders/user/{user_id}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                user_data["orders"] = response.json()
                span.set_attribute("orders.count", len(user_data["orders"]))
            else:
                span.set_attribute("orders.error", True)
                user_data["orders"] = []

        except Exception as e:
            span.record_exception(e)
            span.set_attribute("orders.error", True)
            logger.error(f"Error calling order service: {e}")
            user_data["orders"] = []

        return jsonify(user_data)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "user-service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
