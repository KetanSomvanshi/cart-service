#!/bin/sh

python --version
echo "Current working directory: `pwd`"
echo "App run command args: $@"

run_service() {
  echo "Generated config, starting cart app..."
  env $(cat /code/config/.env | xargs) /usr/local/bin/uvicorn server.app:app --host=0.0.0.0 --port=9999 --workers=4
}

run_service