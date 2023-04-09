#!/bin/sh

python --version
echo "Current working directory: `pwd`"
echo "App run command args: $@"

run_tests() {
  echo "Generated config, starting cart app..."
  env $(cat /code/config/.env | xargs) /usr/local/bin/pytest
}

run_tests