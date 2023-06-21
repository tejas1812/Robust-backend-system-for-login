VERSION=
DOCKERUSER=

build:
	docker build -f Dockerfile -t backend-rbac .

push:
	docker tag backend-rbac $(DOCKERUSER)/backend-rbac:$(VERSION)
	docker push $(DOCKERUSER)/backend-rbac:$(VERSION)
	docker tag backend-rbac $(DOCKERUSER)/backend-rbac:latest
	docker push $(DOCKERUSER)/backend-rbac:latest

deploy:
	kubectl apply -f deployment.yaml
	kubectl apply -f service.yaml