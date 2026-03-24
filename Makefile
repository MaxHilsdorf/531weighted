IMAGE_NAME ?= 531weighted
PORT ?= 8501

.PHONY: build run test format lint

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -p $(PORT):8501 $(IMAGE_NAME)

test:
	uv run pytest

format:
	uv run ruff format

lint:
	uv run ruff check