#!/bin/bash

set -Eeuo pipefail

docker build --tag seeq13/pr-reminders:latest .
