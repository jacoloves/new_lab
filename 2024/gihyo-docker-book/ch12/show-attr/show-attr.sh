#!/bin/sh

ATTR=$1
if [ "$ATTR" = "" ]; then
    echo "required attribute name arugument" 1 >&2
    exit 1
fi

echo '{
    "id": 100,
    "username": "gihyo",
    "comment": "Finally, jq version 1.7 has been released.
}' | jq -r ".$ATTR"