start-todo:
	uvicorn src.main:app --reload --port 8000

lint:
	ruff check --fix
