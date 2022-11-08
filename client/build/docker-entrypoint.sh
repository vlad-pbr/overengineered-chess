#!/usr/bin/env bash

# substitute parameters
envsubst < /usr/share/nginx/html/env.json > /tmp/env.json
mv /tmp/env.json /usr/share/nginx/html/env.json

# run nginx as usual
exec /docker-entrypoint.sh "$@"