from flask import Flask, request, jsonify
import requests
import logging
import random
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry.sdk.resources import Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

resource = Resource.create({"service.name": "order-service", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/orders/user/<user_id>')
def get_user_orders(user_id):
    context = extract(request.headers)
    with tracer.start_as_current_span("get_user_orders", context=context) as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("service.name", "order-service")
        logger.info(f"Processing order request for user: {user_id}")

        time.sleep(random.uniform(0.1, 0.3))

        orders = []
        order_count = random.randint(1, 3)

        for i in range(order_count):
            order_id = f"order_{user_id}_{i + 1}"
            with tracer.start_as_current_span("process_individual_order") as order_span:
                order_span.set_attribute("order.id", order_id)
                try:
                    headers = {}
                    inject(headers)
                    response = requests.get(
                        f"http://localhost:5003/inventory/order/{order_id}",
                        headers=headers,
                        timeout=5
                    )
                    if response.status_code == 200:
                        inventory_data = response.json()
                        order_span.set_attribute("inventory.available", inventory_data.get("available", False))
                    else:
                        inventory_data = {"available": False, "error": "service_unavailable"}
                        order_span.set_attribute("inventory.error", True)
                except Exception as e:
                    order_span.record_exception(e)
                    logger.error(f"Error calling inventory service: {e}")
                    inventory_data = {"available": False, "error": str(e)}

                orders.append({
                    "id": order_id,
                    "user_id": user_id,
                    "amount": round(random.uniform(10.0, 500.0), 2),
                    "status": "completed",
                    "inventory": inventory_data
                })

        span.set_attribute("orders.count", len(orders))
        return jsonify(orders)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "order-service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
