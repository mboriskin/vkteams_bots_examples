IMAGE_NAME = the_serious_bot_image
SERVICE_NAME = serious_bot
ENV_PYTHON_VERSION = 3.11

STAGE = stage
STABLE = stable

CONFIG_TEMPLATE = /etc/config.yaml.j2


build_stage:
	docker rmi -f $(IMAGE_NAME)_$(STAGE) || true
	docker builder prune -f || true
	docker build --network=host -t $(IMAGE_NAME)_$(STAGE) \
	--build-arg STAGE=$(STAGE) \
	--build-arg VKT_BOT_TOKEN=$(VKT_BOT_TOKEN) \
	--build-arg JIRA_TOKEN=$(JIRA_TOKEN) \
	--build-arg VKT_BOT_ID=$(VKT_BOT_ID) \
	--build-arg GITLAB_TOKEN=$(GITLAB_TOKEN) \
	.

run_stage:
	docker run -d --network host \
	--name $(SERVICE_NAME)_$(STAGE) \
	-v /data/serious_bot/db_stage/database.db:/etc/database.db \
	--env CONFIG_TEMPLATE=$(CONFIG_TEMPLATE) \
	--env PYTHONUNBUFFERED=1 \
	$(IMAGE_NAME)_$(STAGE) \
	/bin/bash -c \
	'python${ENV_PYTHON_VERSION} -m pip install --no-cache-dir serious-bot-${STAGE} \
	&& python${ENV_PYTHON_VERSION} -m ${SERVICE_NAME}.${SERVICE_NAME}' \
	/bin/bash

stop_stage:
	docker stop $(SERVICE_NAME)_$(STAGE) || true
	docker rm $(SERVICE_NAME)_$(STAGE) || true

rebuild_stage: stop_stage build_stage run_stage


build:
	docker rmi -f $(IMAGE_NAME)_$(STABLE) || true
	docker builder prune -f || true
	docker build --network=host -t $(IMAGE_NAME)_$(STABLE) \
	--build-arg STAGE=$(STABLE) \
	--build-arg VKT_BOT_TOKEN=$(VKT_BOT_TOKEN) \
	--build-arg JIRA_TOKEN=$(JIRA_TOKEN) \
	--build-arg VKT_BOT_ID=$(VKT_BOT_ID) \
	--build-arg GITLAB_TOKEN=$(GITLAB_TOKEN) \
	.

run:
	docker run -d --network host \
	--name $(SERVICE_NAME)_$(STABLE) \
	-v /data/serious_bot/db_stable/database.db:/etc/database.db \
	--env CONFIG_TEMPLATE=$(CONFIG_TEMPLATE) \
	--env PYTHONUNBUFFERED=1 \
	$(IMAGE_NAME)_$(STABLE) \
	/bin/bash -c \
	'python${ENV_PYTHON_VERSION} -m pip install --no-cache-dir serious-bot-${STABLE} \
	&& python${ENV_PYTHON_VERSION} -m ${SERVICE_NAME}.${SERVICE_NAME}' \
	/bin/bash

stop:
	docker stop $(SERVICE_NAME)_$(STABLE) || true
	docker rm $(SERVICE_NAME)_$(STABLE) || true

rebuild: stop build run
