start-todo:
	uvicorn src.main:app --reload --port 8001

lint:
	ruff check --fix
