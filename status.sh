#!/bin/bash

PID=$(pgrep -f "python3 app.py")

if [ -z "$PID" ]; then
    echo "ToolMong is NOT running."
else
    echo "ToolMong is running."
    ps -fp $PID
fi
