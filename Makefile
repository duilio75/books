# Build and run the Django app in Docker, connecting to Postgres on the host.
#
# Inside the container "localhost" is the container itself, so DB_HOST is
# overridden to host.docker.internal at runtime (mapped to the host gateway).
# Everything else comes from .env, which is intentionally not baked into the image.

IMAGE := tb-backend
PORT  := 8000

.PHONY: build run up sh logs

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm -p $(PORT):$(PORT) \
		--add-host=host.docker.internal:host-gateway \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
		$(IMAGE)

# Build then run in one step
up: build run

# Open a shell in a throwaway container (handy for debugging)
sh:
	docker run --rm -it \
		--add-host=host.docker.internal:host-gateway \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
		$(IMAGE) /bin/sh
