#!/bin/bash
docker-entrypoint.sh postgres  &
sleep 5 &&\
su postgres -c "createdb TEST" &&\
echo "Im super cool" &&\
cd /opt/code/
dagster-daemon run &
dagster job execute -m weather -j prebuild_locations_job -d /opt/code -c /opt/code/config/prebuild.yaml &
dagit -h 0.0.0.0 -p 3000 -w /opt/code/workspace.yaml
