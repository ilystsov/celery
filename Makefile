run:
	cp -n .env.example .env || true
	docker-compose up tasks-app

test:
	pytest tests
