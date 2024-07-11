#!/bin/bash

set -Eeuo pipefail

image_name="seeq13/pr-reminders"
docker build --tag "$image_name":latest .
if [[ $# -eq 1 ]]; then
    version="$1"
    docker tag "$image_name":latest "$image_name":"$version"

    # package the Helm chart
    rm -rf build
    mkdir -p build
    cp -R helm build/chart
    gsed -e "s/{{ version }}/$version/g" -i'' build/chart/Chart.yaml
    helm package build/chart --destination build
fi

