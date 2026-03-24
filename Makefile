IMAGE_NAME ?= 531weighted
PORT ?= 8501

.PHONY: build run test format format-check lint

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -p $(PORT):8501 $(IMAGE_NAME)

test:
	uv run pytest

format:
	uv run ruff format

format-check:
	uv run ruff format --check

lint:
	uv run ruff check