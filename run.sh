#!/bin/bash

set -Eeuo pipefail

eval "$(dotenv list)"
echo "$PR_REMINDERS_CONFIG_PATH"
config_path="$(readlink -f "$PR_REMINDERS_CONFIG_PATH")"
docker run \
    --env-file ./.env \
    --env PR_REMINDERS_CONFIG_PATH=/app/config/config.json \
    --mount "type=bind,source=$config_path,target=/app/config/config.json" \
    seeq13/pr-reminders:latest
