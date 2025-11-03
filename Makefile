.PHONY: all build deploy smoke down clean reset nuke prune help

NS        ?= dev 					# Namespace
CLUSTER   ?= opsbox 				# Cluser name
API_IMAGE ?= opsbox-api:dev			# Api image
WRK_IMAGE ?= opsbox-worker:dev		# Worker image
OPTION	  ?= ""						# Deploy option

all:
	$(info  ⚡ Running all build deploy and smoke...)
	$(MAKE) build deploy smoke

build:
	$(info    ⚡ Building images...)
	docker build -f api/Dockerfile -t opsbox-api:dev .
	docker build -f worker/Dockerfile -t opsbox-worker:dev .

deploy:
	@echo "Deploy with argocd? (y/N):" && read ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ] || [ "$$ans" = "yes" ] || [ "$$ans" = "YES" ]; then \
		OPTION="--argocd"; \
	else \
		OPTION=""; \
	fi; \
	$(info    ⚡ Deploying application...) \
	./ops/scripts/bootstrap.sh $$OPTION

smoke:
	$(info    ⚡ Starting smoke tests...)
	curl -sf http://127.0.0.1:8080/health
	kubectl -n dev exec -it sts/redis-master -- redis-cli PING
	kubectl -n dev run redistest --rm -it --image=alpine:3.19 -- sh -lc 'apk add -q --no-progress redis; redis-cli -h redis-master -p 6379 PING'

kill-pf:
	$(info    ⚡ Stopping port-forwarding...)
	-pkill -f "kubectl -n $(NS) port-forward svc/api 8080:80" || true

down: kill-pf
	$(info    ⚡ Tearing down application...)
	./ops/scripts/teardown.sh

clean:
	$(info    ⚡ Cleaning up...)
	-docker rmi -f $(API_IMAGE) $(WRK_IMAGE) 2>/dev/null || true
	-docker image prune -f

reset: down clean

nuke: clean
	$(info    ⚡ Deleting kind cluster...)
	./ops/scripts/teardown.sh --delete-cluster

prune:
	-docker system prune -f

help:
	@echo "Targets:"
	@echo "  build   - build API & worker images"
	@echo "  deploy  - bootstrap kind, DB/queue, API & worker"
	@echo "  smoke   - hit /health"
	@echo "  down    - uninstall Helm releases, delete namespace, kill port-forward"
	@echo "  clean   - remove local images + prune dangling layers"
	@echo "  reset   - down + clean"
	@echo "  nuke    - reset + delete kind cluster"
	@echo "  prune   - docker system prune"
