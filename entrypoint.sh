#!/bin/bash
docker-entrypoint.sh postgres  &
sleep 5 &&\
su postgres -c "createdb TEST" &&\
echo "Im super cool" &&\
dagster-daemon run &
dagit -h 0.0.0.0 -p 3000 -w /opt/code/workspace.yaml
