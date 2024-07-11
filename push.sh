#!/bin/bash

set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: push.sh version"
    exit 1
fi

image_name="seeq13/pr-reminders"
version="$1"
docker push "$image_name":latest
docker push "$image_name":"$version"

helm_chart_name="pr-reminders-helm"
helm push build/"$helm_chart_name"-"$version".tgz oci://registry-1.docker.io/seeq13
