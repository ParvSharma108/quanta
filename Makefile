.PHONY: help install test test-ai run-ai run-example docker-up docker-down

help:
	@echo "QUANTA Developer Commands:"
	@echo "  make install         - Install AI engine Python dependencies"
	@echo "  make test-ai         - Run AI engine test suite (pytest)"
	@echo "  make run-ai          - Start FastAPI AI engine service on port 8000"
	@echo "  make run-example     - Run synthetic ₹100 Cr capital allocation benchmark"
	@echo "  make docker-up       - Launch all services with docker-compose"
	@echo "  make docker-down     - Tear down docker-compose services"

install:
	pip install -r services/ai-engine/requirements.txt

test-ai:
	cd services/ai-engine && pytest -v

run-ai:
	cd services/ai-engine && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-example:
	python services/ai-engine/examples/basic_capital_allocation.py

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
