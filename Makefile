# Makefile

PROJECT_ID := $(shell cat .env | grep PROJECT_ID | cut -d'=' -f2)
REGION := $(shell cat .env | grep REGION | cut -d'=' -f2)
SERVICE_NAME := discordbot
IMAGE_NAME := gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)
LOCAL_IMAGE_NAME := $(SERVICE_NAME)
DISCORD_BOT_TOKEN := $(shell cat .env | grep DISCORD_BOT_TOKEN | cut -d'=' -f2)
TARGET_PLATFORM := linux/amd64

# Local run
local:
	python main.py

local-docker:
	docker run --env PORT=8080 --env-file .env -p 8080:8080 $(IMAGE_NAME)

# Build Docker image
build:
	docker buildx build --platform $(TARGET_PLATFORM) -t $(IMAGE_NAME) .

# Push Docker image to Google Container Registry (if deploying to Cloud Run)
push:
	docker push $(IMAGE_NAME)

# Deploy to Cloud Run (if desired)
deploy:
	gcloud config set project $(PROJECT_ID)
	gcloud config set run/region $(REGION)
	gcloud run deploy $(SERVICE_NAME) --image $(IMAGE_NAME) --platform managed --region $(REGION) --allow-unauthenticated

# Clean up Docker images
clean:
	docker rmi $(LOCAL_IMAGE_NAME)

run:
	docker run --env PORT=8080 --env-file .env -p 8080:8080 $(LOCAL_IMAGE_NAME)

.PHONY: local build push deploy clean run
