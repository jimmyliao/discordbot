# Makefile

PROJECT_NAME := discordbot
IMAGE_NAME := $(PROJECT_NAME)

run:
	python main.py

build:
	docker build -t $(IMAGE_NAME) .

clean:
	docker rmi $(IMAGE_NAME)

.PHONY: run build clean
