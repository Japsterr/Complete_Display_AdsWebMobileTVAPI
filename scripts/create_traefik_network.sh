#!/bin/sh
# Create a Docker network named 'traefik' used by the Traefik stack.
# Usage: on host with Docker installed: sudo sh create_traefik_network.sh

if docker network inspect traefik >/dev/null 2>&1; then
  echo "Network 'traefik' already exists"
  exit 0
fi

echo "Creating network 'traefik'..."
docker network create traefik && echo "Network 'traefik' created" || echo "Failed to create network 'traefik'"
