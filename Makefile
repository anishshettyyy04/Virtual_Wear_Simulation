.PHONY: run test smoke validate benchmark report clean help

help:
	@echo "AI Virtual Wear Simulation — Developer Commands"
	@echo "------------------------------------------------"
	@echo "make run        - Start FastAPI dev server"
	@echo "make test       - Run unit and API integration tests"
	@echo "make smoke      - Run automated smoke test suite"
	@echo "make validate   - Validate JSON datasets against schemas"
	@echo "make benchmark  - Run recommendation engine benchmark"
	@echo "make report     - Generate latency & performance report"

run:
	python -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --reload

test:
	python backend/tests/test_api.py
	python backend/tests/test_recommendation.py

smoke:
	python backend/tests/test_smoke.py

validate:
	python backend/scripts/validate_products.py
	python backend/scripts/validate_user_preferences.py

benchmark:
	python backend/scripts/benchmark_recommendation.py

report:
	python backend/scripts/performance_report.py
