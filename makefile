up:
	docker-compose up -d

build:
	docker-compose build

install:
	docker-compose up -d --build

bash-app:
	docker exec -it app bash	

down:
	docker-compose down