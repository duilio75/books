# Build and run the Django app in Docker, connecting to Postgres on the host.
#
# The container shares the host network namespace (--network host), so
# "localhost" inside the container is the host: DB_HOST=localhost from .env
# reaches Postgres on 127.0.0.1:5432 without opening it to the docker bridge.
# The app binds the host's $(PORT) directly, so no -p mapping is needed.
# Linux only; on macOS/Windows use --add-host=host.docker.internal:host-gateway
# with -e DB_HOST=host.docker.internal instead.
# Everything else comes from .env, which is intentionally not baked into the image.

IMAGE := tb-backend
PORT  := 8075
# With --network host there is no port mapping, so PORT is passed straight to
# gunicorn's --bind. Override per run if it's taken: make run PORT=8081
# Named volume holding user uploads (MEDIA_ROOT=/app/media); survives rebuilds.
MEDIA_VOLUME := tb-media
# Where media snapshots are written/read on the host.
BACKUP_DIR  := backup
BACKUP_FILE := media.tgz

.PHONY: build run up sh logs backup-media backup-media-dated restore-media

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm \
		--network host \
		--env-file .env \
		-v $(MEDIA_VOLUME):/app/media \
		$(IMAGE) \
		gunicorn backend.wsgi:application --bind 0.0.0.0:$(PORT) --workers 3

# Build then run in one step
up: build run

# Open a shell in a throwaway container (handy for debugging)
sh:
	docker run --rm -it \
		--network host \
		--env-file .env \
		-v $(MEDIA_VOLUME):/app/media \
		$(IMAGE) /bin/sh

# Snapshot the media volume into $(BACKUP_DIR)/$(BACKUP_FILE) on the host.
# Mounted read-only so the running app can't be disturbed by the backup.
backup-media:
	mkdir -p $(BACKUP_DIR)
	docker run --rm \
		-v $(MEDIA_VOLUME):/data:ro \
		-v $(CURDIR)/$(BACKUP_DIR):/backup \
		alpine tar czf /backup/$(BACKUP_FILE) -C /data .
	@echo "Backed up media volume '$(MEDIA_VOLUME)' to $(BACKUP_DIR)/$(BACKUP_FILE)"

# Like backup-media, but writes a timestamped archive so snapshots never
# overwrite each other. The timestamp is evaluated on the host at run time.
backup-media-dated: STAMP := $(shell date +%Y-%m-%d_%H-%M-%S)
backup-media-dated:
	mkdir -p $(BACKUP_DIR)
	docker run --rm \
		-v $(MEDIA_VOLUME):/data:ro \
		-v $(CURDIR)/$(BACKUP_DIR):/backup \
		alpine tar czf /backup/media-$(STAMP).tgz -C /data .
	@echo "Backed up media volume '$(MEDIA_VOLUME)' to $(BACKUP_DIR)/media-$(STAMP).tgz"

# Restore the media volume from $(BACKUP_DIR)/$(BACKUP_FILE), replacing its contents.
# Stop the app first so nothing writes mid-restore.
restore-media:
	@test -f $(BACKUP_DIR)/$(BACKUP_FILE) || { echo "No backup at $(BACKUP_DIR)/$(BACKUP_FILE)"; exit 1; }
	docker run --rm \
		-v $(MEDIA_VOLUME):/data \
		-v $(CURDIR)/$(BACKUP_DIR):/backup \
		alpine sh -c "find /data -mindepth 1 -delete && tar xzf /backup/$(BACKUP_FILE) -C /data"
	@echo "Restored media volume '$(MEDIA_VOLUME)' from $(BACKUP_DIR)/$(BACKUP_FILE)"
