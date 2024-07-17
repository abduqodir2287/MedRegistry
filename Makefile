start-todo:
	uvicorn src.main:app --reload --port 8005

lint:
	ruff check --fix
