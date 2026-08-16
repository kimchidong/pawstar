#!/bin/bash

PID=$(pgrep -f "python3 app.py")

if [ -z "$PID" ]; then
    echo "PawStar is NOT running."
else
    echo "PawStar is running."
    ps -fp $PID
fi
