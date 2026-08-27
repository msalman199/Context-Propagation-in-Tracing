#!/bin/bash
source venv/bin/activate

cd services/inventory-service
python3 app.py > ~/tracing-lab/inventory.log 2>&1 &
echo $! > ~/tracing-lab/inventory.pid

cd ../order-service
python3 app.py > ~/tracing-lab/order.log 2>&1 &
echo $! > ~/tracing-lab/order.pid

cd ../user-service
python3 app.py > ~/tracing-lab/user.log 2>&1 &
echo $! > ~/tracing-lab/user.pid

echo "Services starting. Waiting 5 seconds..."
sleep 5
echo "user-service:      http://localhost:5001"
echo "order-service:     http://localhost:5002"
echo "inventory-service: http://localhost:5003"
