#!/bin/bash
echo "=== System Status Monitor ==="
echo "Started at: $(date)"
echo ""

while true; do
    echo "--- $(date '+%H:%M:%S') ---"
    
    # Check container status
    docker-compose ps
    
    # Check for API health
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo 'API Health: OK'
    else
        echo 'API Health: NOT READY'
    fi
    
    # Get last 5 lines of API logs if container exists
    if docker ps -a --format '{{.Names}}' | grep -q verse-api; then
        echo 'API Logs (last 5):'
        docker-compose logs --tail 5 api 2>&1 | tail -10
    fi
    
    echo ""
    sleep 30
done