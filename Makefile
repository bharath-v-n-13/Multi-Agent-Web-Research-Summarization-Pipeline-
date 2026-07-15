.PHONY: build up down run test clean verify

# Variables
DOCKER_COMPOSE = docker-compose

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down --remove-orphans

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	rm -rf reports/* logs/* .pytest_cache

test:
	$(DOCKER_COMPOSE) run --rm api pytest -v

run: down build
	@echo "Starting up infrastructure (Redis, FastAPI, and Agent Workers)..."
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for FastAPI service liveness check on port 8000..."
	@for i in {1..30}; do \
		curl -s http://localhost:8000/health && break; \
		echo "Waiting... ($$i/30)"; \
		sleep 2; \
	done
	@echo ""
	@echo "Executing autonomous research query on: 'Future of Quantum Computing'..."
	curl -s -X POST "http://localhost:8000/research" \
		-H "Content-Type: application/json" \
		-d '{"topic": "Future of Quantum Computing", "depth": "shallow", "max_sources": 5, "output_format": "json"}' > reports/demo_run.json
	@echo ""
	@echo "Query completed. Result saved to reports/demo_run.json."
	@echo ""
	@echo "Verifying schema correctness..."
	./verify.sh
