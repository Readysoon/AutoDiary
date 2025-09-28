# AutoDiary Makefile

.PHONY: start stop restart db agent clean

# Start everything: database + scraper + agent
start:
	@echo "Starting SurrealDB..."
	docker compose up -d surrealdb
	@echo "Waiting for database to be ready..."
	sleep 3
	@echo "Running WhatsApp scraper..."
	source venv/bin/activate && python -c "import asyncio; from whatsapp_scraper.main import collect_todays_messages; asyncio.run(collect_todays_messages())" &
	@echo "Scraper started in background, now starting LiveKit Agent..."
	sleep 2
	source venv/bin/activate && python agent.py console

# Start only database
db:
	@echo "Starting SurrealDB only..."
	docker compose up surrealdb

# Start only agent (assumes DB is running)
agent:
	@echo "Starting LiveKit Agent..."
	source venv/bin/activate && python agent.py console

# Start only scraper (assumes DB is running)
scraper:
	@echo "Starting WhatsApp scraper..."
	source venv/bin/activate && python -c "import asyncio; from whatsapp_scraper.main import collect_todays_messages; asyncio.run(collect_todays_messages())"

# Stop all services
stop:
	@echo "Stopping all services..."
	@echo "Stopping LiveKit Agent processes..."
	-pkill -f "python agent.py" || true
	@echo "Stopping WhatsApp scraper processes..."
	-pkill -f "collect_todays_messages" || true
	@echo "Stopping Docker containers..."
	docker compose down
	@echo "All services stopped"

# Restart everything
restart: stop start

# Clean up Docker resources
clean:
	@echo "Cleaning up Docker resources..."
	docker compose down --volumes --remove-orphans
	docker system prune -f

# Show help
help:
	@echo "Available commands:"
	@echo "  make start    - Start database and agent"
	@echo "  make db       - Start only database"
	@echo "  make agent    - Start only agent"
	@echo "  make stop     - Stop all services"
	@echo "  make restart  - Restart everything"
	@echo "  make clean    - Clean up Docker resources"
	@echo "  make help     - Show this help"
