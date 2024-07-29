start-service:
	uvicorn src.main:app --reload --port 8001

lint:
	ruff check --fix

alembic-upg:
	python -m alembic upgrade head

