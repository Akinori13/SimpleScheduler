.PHONY: app-up
app-up:
	docker-compose up -d

.PHONY: app-build
app-build:
	docker-compose build

.PHONY: app-install
app-install:
	docker-compose up -d --build

.PHONY: app-down
app-down:
	docker-compose down

.PHONY: app-restart
app-restart:
	docker-compose down
	docker-compose build
	docker-compose up -d

.PHONY: django-exec
django-exec:
	docker exec -it django_wsgi bash

.PHONY: ui-tests
ui-tests:
	docker exec django_wsgi python manage.py test accounts.tests.SeleniumTests

.PHONY: django-tests
django-tests:
	docker exec django_wsgi python manage.py test accounts.tests.TestSignup
