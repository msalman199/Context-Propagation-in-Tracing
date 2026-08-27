# 🔗 Context Propagation in Distributed Tracing

> 🚀 A hands-on lab for understanding distributed tracing and implementing **W3C Trace Context propagation** across multiple microservices using **OpenTelemetry, Flask, Docker, and Jaeger**.

---

## 📌 Table of Contents

* 🎯 Lab Objectives
* 🛠️ Technologies Used
* 📋 Prerequisites
* 🏗️ Architecture
* 🔧 Environment Setup
* 🔍 Jaeger Tracing Backend
* 🚀 Three-Service Architecture
* 🔗 Context Propagation
* ▶️ Running the Services
* 🧪 Testing Distributed Traces
* 📊 Verifying Traces in Jaeger
* 🛠️ Troubleshooting
* 🎓 Conclusion

---

# 🎯 Lab Objectives

By completing this lab, you will be able to:

* ✅ Understand the importance of trace context propagation
* 🔗 Implement the **W3C Trace Context** standard
* 📡 Configure OpenTelemetry with Flask and Requests
* 🚀 Track a distributed request across three microservices
* 🔍 Analyze distributed traces in Jaeger
* ⏱️ Identify latency across the request chain

---

# 🛠️ Technologies Used

<p align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge\&logo=python)
![Flask](https://img.shields.io/badge/Flask-Microservices-black?style=for-the-badge\&logo=flask)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Distributed_Tracing-blue?style=for-the-badge)
![Jaeger](https://img.shields.io/badge/Jaeger-Tracing-orange?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containers-blue?style=for-the-badge\&logo=docker)
![Linux](https://img.shields.io/badge/Linux-Environment-yellow?style=for-the-badge\&logo=linux)

</p>

---

# 📋 Prerequisites

Before starting this lab, you should have:

* 🐧 Basic Linux command-line knowledge
* 🌐 Understanding of HTTP requests and responses
* 🐍 Basic Python programming knowledge
* 🏗️ Familiarity with microservices architecture
* 🐳 Basic Docker knowledge

---

# 🏗️ Architecture

This lab implements three cooperating microservices.

```text
                    ┌───────────────────┐
                    │   User Service    │
                    │    Port: 5001     │
                    └─────────┬─────────┘
                              │
                     HTTP Request + Context
                              │
                              ▼
                    ┌───────────────────┐
                    │   Order Service   │
                    │    Port: 5002     │
                    └─────────┬─────────┘
                              │
                     HTTP Request + Context
                              │
                              ▼
                    ┌───────────────────┐
                    │ Inventory Service │
                    │    Port: 5003     │
                    └─────────┬─────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   Jaeger    │
                       │ Distributed │
                       │   Tracing   │
                       └─────────────┘
```

Each service contributes spans to the same distributed trace.

---

# 🔗 How Context Propagation Works

Context propagation allows a request to maintain the same trace identity while moving between services.

```text
Client Request
      │
      ▼
User Service
Trace ID: ABC123
      │
      │ inject(headers)
      ▼
Order Service
Trace ID: ABC123
      │
      │ inject(headers)
      ▼
Inventory Service
Trace ID: ABC123
      │
      ▼
Jaeger
```

The receiving services use:

```python
extract(request.headers)
```

The sending services use:

```python
inject(headers)
```

This allows all services to share a single distributed trace.

---

# 🔧 Environment Setup

## 🐳 Install Required Packages

```bash
sudo apt update

sudo apt install -y \
python3 \
python3-pip \
python3-venv \
curl \
docker.io \
docker-compose
```

Start and enable Docker:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Add the current user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Verify the installation:

```bash
docker --version
docker-compose --version
```

---

# 📁 Create the Lab Environment

Create the project directory:

```bash
mkdir -p ~/tracing-lab
cd ~/tracing-lab
```

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

Install the required dependencies:

```bash
pip install flask==3.0.3 requests==2.32.3 \
opentelemetry-api==1.27.0 \
opentelemetry-sdk==1.27.0 \
opentelemetry-instrumentation-flask==0.48b0 \
opentelemetry-instrumentation-requests==0.48b0 \
opentelemetry-exporter-jaeger==1.21.0
```

⚠️ Remember to activate the virtual environment in every new terminal:

```bash
source ~/tracing-lab/venv/bin/activate
```

---

# 🔍 Task 1: Set Up Jaeger

## 🐳 Create Docker Compose Configuration

Create the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:1.58

    ports:
      - "16686:16686"
      - "14268:14268"
      - "6831:6831/udp"
      - "6832:6832/udp"

    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411

networks:
  default:
    name: tracing-network
```

---

## ▶️ Start Jaeger

```bash
docker-compose up -d
```

Check the container:

```bash
docker-compose ps
```

Verify Jaeger is accessible:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
http://localhost:16686
```

Expected output:

```text
200
```

---

# 🚀 Task 2: Build the Microservices

Create the service directories:

```bash
mkdir -p services/inventory-service
mkdir -p services/order-service
mkdir -p services/user-service
```

---

## 📦 Inventory Service

### Port

```text
5003
```

### Responsibilities

* 📦 Check inventory
* 🗄️ Simulate database operations
* 🔍 Create tracing spans
* 📊 Add inventory attributes
* ⚠️ Generate inventory events

Important span:

```text
check_inventory
```

Nested database span:

```text
database_lookup
```

---

## 🛒 Order Service

### Port

```text
5002
```

### Responsibilities

* 🛒 Process user orders
* 🔗 Call the inventory service
* 📡 Inject trace context into request headers
* 📊 Create order spans

Important propagation process:

```python
headers = {}

inject(headers)

response = requests.get(
    inventory_service_url,
    headers=headers
)
```

---

## 👤 User Service

### Port

```text
5001
```

The User Service is the entry point of the application.

### Responsibilities

* 👤 Process user requests
* 🛒 Call the order service
* 🔗 Propagate tracing context
* 📊 Collect user and order information

The request flow starts with:

```text
GET /user/<user_id>
```

---

# 🔗 W3C Trace Context

The W3C Trace Context standard allows trace information to move between distributed services.

The main concept is the:

```text
traceparent
```

header.

The complete request flow is:

```text
Client
  │
  ▼
User Service
  │
  │ traceparent
  ▼
Order Service
  │
  │ traceparent
  ▼
Inventory Service
```

The trace context ensures that all spans belong to the same distributed request.

---

# 🔄 Inject and Extract Context

## 📤 Sending Context

Before making an HTTP request:

```python
headers = {}

inject(headers)
```

Then pass the headers:

```python
requests.get(
    url,
    headers=headers
)
```

---

## 📥 Receiving Context

The receiving service extracts the context:

```python
context = extract(request.headers)
```

The context is then passed to the tracing span:

```python
with tracer.start_as_current_span(
    "operation_name",
    context=context
):
    pass
```

This maintains the parent-child relationship between spans.

---

# ▶️ Task 3: Run the Services

You can start the services using separate terminals.

## 🖥️ Terminal 1 — Inventory Service

```bash
cd ~/tracing-lab
source venv/bin/activate

cd services/inventory-service
python3 app.py
```

---

## 🖥️ Terminal 2 — Order Service

```bash
cd ~/tracing-lab
source venv/bin/activate

cd services/order-service
python3 app.py
```

---

## 🖥️ Terminal 3 — User Service

```bash
cd ~/tracing-lab
source venv/bin/activate

cd services/user-service
python3 app.py
```

---

# ⚙️ Alternative: Start All Services with a Script

Create:

```text
start_services.sh
```

The script can:

* 🚀 Start Inventory Service
* 🛒 Start Order Service
* 👤 Start User Service
* 📜 Save logs
* 🆔 Store process IDs

Make it executable:

```bash
chmod +x start_services.sh
```

Run it:

```bash
./start_services.sh
```

---

# 🛑 Stop the Services

Create:

```text
stop_services.sh
```

Make it executable:

```bash
chmod +x stop_services.sh
```

The script stops all services using their stored process IDs.

---

# ❤️ Verify Service Health

Check the User Service:

```bash
curl -s http://localhost:5001/health
```

Check the Order Service:

```bash
curl -s http://localhost:5002/health
```

Check the Inventory Service:

```bash
curl -s http://localhost:5003/health
```

Expected result:

```json
{
  "service": "service-name",
  "status": "healthy"
}
```

---

# 🧪 Generate a Distributed Trace

Send a request to the User Service:

```bash
curl -s http://localhost:5001/user/1001 | python3 -m json.tool
```

The request travels through:

```text
User Service
      │
      ▼
Order Service
      │
      ▼
Inventory Service
```

The final response contains:

* 👤 User information
* 🛒 Orders
* 📦 Inventory information

---

# 🔄 Generate Multiple Requests

Generate more requests:

```bash
for i in 1 2 3 4 5; do
  curl -s \
  "http://localhost:5001/user/200$i" \
  > /dev/null

  sleep 1
done
```

This generates multiple traces for analysis.

---

# 📊 Verify Traces in Jaeger

Check registered services:

```bash
curl -s \
"http://localhost:16686/api/services" \
| python3 -m json.tool
```

Expected services:

```text
user-service
order-service
inventory-service
```

---

## 🔍 Check Trace Data

Query recent traces:

```bash
curl -s \
"http://localhost:16686/api/traces?service=user-service&limit=5" \
| python3 -m json.tool
```

Verify that the trace contains spans from:

* 👤 `user-service`
* 🛒 `order-service`
* 📦 `inventory-service`

Most importantly, all related spans should share the same:

```text
traceID
```

This proves that context propagation is working correctly.

---

# 🖥️ Jaeger UI

Open Jaeger:

```text
http://localhost:16686
```

Steps:

1. 🔍 Select **user-service**
2. 📊 Click **Find Traces**
3. 🕒 Open the latest trace
4. 🔗 Verify all services belong to the same trace
5. 📈 Analyze the span hierarchy

You should see nested operations such as:

```text
get_user_operation
       │
       ▼
get_user_orders
       │
       ▼
process_individual_order
       │
       ▼
check_inventory
       │
       ▼
database_lookup
```

---

# 🛠️ Troubleshooting

## ⚠️ Problem: Traces Do Not Connect

### Possible Cause

The trace context is not being propagated.

### Solution

Verify that outgoing requests use:

```python
inject(headers)
```

Verify that receiving services use:

```python
extract(request.headers)
```

Then ensure the extracted context is used when creating the new span.

---

## ⚠️ Problem: Service Connection Error

Check whether all services are running:

```bash
ps aux | grep app.py
```

Check the required ports:

```bash
ss -tlnp | grep -E '5001|5002|5003'
```

Make sure:

* User Service is running on `5001`
* Order Service is running on `5002`
* Inventory Service is running on `5003`

---

# 🎯 Expected Outcomes

After completing this lab, you should have:

* ✅ Three independently running Flask microservices
* 🔗 Automatic W3C Trace Context propagation
* 📡 OpenTelemetry instrumentation
* 🔍 Distributed traces stored in Jaeger
* 🆔 A single `traceID` spanning all three services
* 📊 Correct parent-child span relationships
* ⏱️ Practical experience identifying latency across services

---

# 🏆 Complete Distributed Tracing Flow

```text
┌──────────────┐
│    Client    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│   User Service   │
│    Port 5001     │
└──────┬───────────┘
       │
       │ inject()
       ▼
┌──────────────────┐
│  Order Service   │
│    Port 5002     │
└──────┬───────────┘
       │
       │ inject()
       ▼
┌──────────────────┐
│Inventory Service │
│    Port 5003     │
└──────┬───────────┘
       │
       │
       ▼
┌──────────────────┐
│      Jaeger      │
│ Distributed Trace│
└──────────────────┘
```

---

# 🎓 Conclusion

🎉 In this lab, you built a complete three-service distributed system using **Flask** and **OpenTelemetry**.

You learned how to:

* 🔗 Propagate trace context between microservices
* 📡 Use OpenTelemetry instrumentation
* 📤 Inject context into outgoing HTTP requests
* 📥 Extract context from incoming requests
* 🆔 Maintain a single trace across multiple services
* 🔍 Analyze distributed traces using Jaeger
* ⏱️ Identify latency and bottlenecks across service boundaries

Context propagation is a fundamental part of distributed tracing. Without it, services produce isolated traces that cannot accurately represent the complete path of a request through a microservices architecture.

---

## 👨‍💻 Author

**Hafiz Muhammad Salman**

### ☁️ Cloud DevOps Engineer | Linux Administrator

---

<p align="center">

⭐ If you found this lab useful, consider giving the repository a star!

🚀 **Happy Tracing!** 🔗🔍

</p>
