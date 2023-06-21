VERSION=
DOCKERUSER=

build:
	docker build -f Dockerfile -t auth-and-auth .

push:
	docker tag auth-and-auth $(DOCKERUSER)/auth-and-auth:$(VERSION)
	docker push $(DOCKERUSER)/auth-and-auth:$(VERSION)
	docker tag auth-and-auth $(DOCKERUSER)/auth-and-auth:latest
	docker push $(DOCKERUSER)/auth-and-auth:latest

deploy:
	kubectl apply -f deployment.yaml
	kubectl apply -f service.yaml