run:
	cp -n .env.example .env || true
	docker-compose up tasks-app

install:
	poetry install

test:
	poetry run pytest tests
