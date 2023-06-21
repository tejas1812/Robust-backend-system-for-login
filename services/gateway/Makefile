VERSION=
DOCKERUSER=

build:
	docker build -f Dockerfile -t gateway .

push:
	docker tag gateway $(DOCKERUSER)/gateway:$(VERSION)
	docker push $(DOCKERUSER)/gateway:$(VERSION)
	docker tag gateway $(DOCKERUSER)/gateway:latest
	docker push $(DOCKERUSER)/gateway:latest

deploy:
	kubectl apply -f deployment.yaml
	kubectl apply -f service.yaml
