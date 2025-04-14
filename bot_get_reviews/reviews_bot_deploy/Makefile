IMAGE_NAME = the_reviews_bot_image
SERVICE_NAME = reviews_bot
ENV_PYTHON_VERSION = 3.11

STAGE = stage
STAGE_CHAT = 98765@chat.agent

STABLE = stable
STABLE_CHAT = 56789@chat.agent

CONFIG_TEMPLATE = /etc/config.yaml.j2


build_stage:
	docker build --network=host -t $(IMAGE_NAME)_$(STAGE) \
	--build-arg STAGE=$(STAGE) \
	--build-arg CHAT=$(STAGE_CHAT) \
	--build-arg VKT_BOT_TOKEN=$(VKT_BOT_TOKEN) \
	--build-arg RUSTORE_PROJECT_KEY=$(RUSTORE_PROJECT_KEY) \
	--build-arg RUSTORE_PROJECT_KEY_ID=$(RUSTORE_PROJECT_KEY_ID) \
	.

run_stage:
	docker run -d --name $(SERVICE_NAME)_$(STAGE) \
	-v /data/reviews_bot/db_stage/database.db:/etc/database.db \
	--env CONFIG_TEMPLATE=$(CONFIG_TEMPLATE) \
	--env PYTHONUNBUFFERED=1 \
	$(IMAGE_NAME)_$(STAGE) \
	/bin/bash -c \
	'python${ENV_PYTHON_VERSION} -m pip install --no-cache-dir reviews-bot-${STAGE} \
	&& python${ENV_PYTHON_VERSION} -m ${SERVICE_NAME}.${SERVICE_NAME}' \
	/bin/bash

stop_stage:
	docker stop $(SERVICE_NAME)_$(STAGE) || true
	docker rm $(SERVICE_NAME)_$(STAGE) || true

rebuild_stage: stop_stage build_stage run_stage


build:
	docker build --network=host -t $(IMAGE_NAME)_$(STABLE) \
	--build-arg STAGE=$(STABLE) \
	--build-arg CHAT=$(STABLE_CHAT) \
	--build-arg VKT_BOT_TOKEN=$(VKT_BOT_TOKEN) \
	--build-arg RUSTORE_PROJECT_KEY=$(RUSTORE_PROJECT_KEY) \
	--build-arg RUSTORE_PROJECT_KEY_ID=$(RUSTORE_PROJECT_KEY_ID) \
	.

run:
	docker run -d --name $(SERVICE_NAME)_$(STABLE) \
	-v /data/reviews_bot/db_stable/database.db:/etc/database.db \
	--env CONFIG_TEMPLATE=$(CONFIG_TEMPLATE) \
	--env PYTHONUNBUFFERED=1 \
	$(IMAGE_NAME)_$(STABLE) \
	/bin/bash -c \
	'python${ENV_PYTHON_VERSION} -m pip install --no-cache-dir reviews-bot-${STABLE} \
	&& python${ENV_PYTHON_VERSION} -m ${SERVICE_NAME}.${SERVICE_NAME}' \
	/bin/bash

stop:
	docker stop $(SERVICE_NAME)_$(STABLE) || true
	docker rm $(SERVICE_NAME)_$(STABLE) || true

rebuild: stop build run
