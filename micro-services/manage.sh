#!/bin/bash

set -e

COMPOSE_FILE="docker-compose.yml"

function usage() {
  echo "Usage: $0 {list|build|destroy}"
  exit 1
}

case "$1" in
  list)
    docker-compose -f "$COMPOSE_FILE" ps
    ;;
  build)
    docker-compose -f "$COMPOSE_FILE" build
    ;;
  destroy)
    docker-compose -f "$COMPOSE_FILE" down
    ;;
  *)
    usage
    ;;
esac