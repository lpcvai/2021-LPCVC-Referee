#!/usr/bin/env bash
pi_server=$1
submission_location=$2
submission_destination=$3

cd "$(dirname "$0")" || exit
echo "$submission_location $pi_server:$submission_destination"
scp "$submission_location" "$pi_server":"$submission_destination"
