#!/bin/bash

PORT=8003

PIDS=$(lsof -t -i:${PORT})

if [ -z "$PIDS" ]; then
    echo "PawStar is not running on port $PORT."
else
    echo "Stopping PawStar processes: $PIDS"

    kill $PIDS

    sleep 2

    PIDS_RECHECK=$(lsof -t -i:${PORT})

    if [ -n "$PIDS_RECHECK" ]; then
        echo "Some processes did not stop. Forcing termination: $PIDS_RECHECK"
        kill -9 $PIDS_RECHECK
    fi

    echo "PawStar stopped."
fi