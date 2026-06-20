# Build and run the Django app in Docker, connecting to Postgres on the host.
#
# Inside the container "localhost" is the container itself, so DB_HOST is
# overridden to host.docker.internal at runtime (mapped to the host gateway).
# Everything else comes from .env, which is intentionally not baked into the image.

IMAGE := tb-backend
PORT  := 8000
# Named volume holding user uploads (MEDIA_ROOT=/app/media); survives rebuilds.
MEDIA_VOLUME := tb-media
# Where media snapshots are written/read on the host.
BACKUP_DIR  := backup
BACKUP_FILE := media.tgz

.PHONY: build run up sh logs backup-media backup-media-dated restore-media

build:
	docker build -t $(IMAGE) .

run:
	docker run --rm -p $(PORT):$(PORT) \
		--add-host=host.docker.internal:host-gateway \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
		-v $(MEDIA_VOLUME):/app/media \
		$(IMAGE)

# Build then run in one step
up: build run

# Open a shell in a throwaway container (handy for debugging)
sh:
	docker run --rm -it \
		--add-host=host.docker.internal:host-gateway \
		--env-file .env \
		-e DB_HOST=host.docker.internal \
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
