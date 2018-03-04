DOCKER_INSTANCE_NAME := dts_client
DOCKER_IMAGE_TAG := dts_client


docker.build:
	docker build -t $(DOCKER_IMAGE_TAG) .

docker.build.nocache:
	docker build --no-cache -t $(DOCKER_IMAGE_TAG) .

docker.run:
	docker run --rm -it --name $(DOCKER_INSTANCE_NAME) -v beasley_client:/var/lib/weewx $(DOCKER_IMAGE_TAG)

