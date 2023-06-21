VERSION=
DOCKERUSER=

build:
	docker build -f Dockerfile -t gateway .

push:
	docker tag login-backend $(DOCKERUSER)/login-backend:$(VERSION)
	docker push $(DOCKERUSER)/login-backend:$(VERSION)
	docker tag login-backend $(DOCKERUSER)/login-backend:latest
	docker push $(DOCKERUSER)/login-backend:latest

deploy:
	kubectl apply -f deployment.yaml
	kubectl apply -f service.yaml