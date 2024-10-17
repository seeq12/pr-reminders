#!/bin/bash

set -Eeuo pipefail

image_name="seeq13/pr-reminders"
docker build --platform=linux/amd64,linux/arm64 --tag "$image_name":latest .
if [[ $# -eq 1 ]]; then
    version="$1"
    docker tag "$image_name":latest "$image_name":"$version"

    # package the Helm chart
    rm -rf build
    mkdir -p build
    cp -R helm build/chart
    sed -e "s/{{ version }}/$version/g" build/chart/Chart.yaml > build/chart/Chart.yaml.tmp
    mv build/chart/Chart.yaml.tmp build/chart/Chart.yaml
    helm package build/chart --destination build
fi

