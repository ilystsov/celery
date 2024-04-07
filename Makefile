run:
	cp -n .env.example .env || true
	docker-compose up tasks-app

install:
	make install

test:
	poetry run pytest tests
