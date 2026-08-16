#!/bin/bash

APP_DIR="/svc/app/toolmong"

cd $APP_DIR

git reset --hard HEAD

git pull

chmod +x $APP_DIR/*.sh
