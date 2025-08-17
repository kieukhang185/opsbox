.PHONY: build deploy smoke

build:
	docker build -t opsbox-api:dev api
	docker build -t opsbox-worker:dev worker

deploy:
	./ops/scripts/bootstrap.sh

smoke:
	curl -sf http://127.0.0.1:8080/health
