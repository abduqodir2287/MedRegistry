start-service:
	uvicorn src.main:app --reload --port 8000

lint:
	ruff check --fix

alembic-upg:
	python -m alembic upgrade head

docker-alembic-upg:
	docker exec -t med_registry-1 python -m alembic upgrade head

test:
	python -m pytest

