#!/bin/bash
for f in inventory.pid order.pid user.pid; do
  if [ -f ~/tracing-lab/$f ]; then
    kill "$(cat ~/tracing-lab/$f)" 2>/dev/null
    rm ~/tracing-lab/$f
  fi
done
echo "All services stopped"
