#!/usr/bin/env bash
pi_server=$1

cd "$(dirname "$0")" || exit
ssh "$pi_server" "mkdir -p .local/bin"
scp bin/pi_firewall "$pi_server":~/.local/bin/
scp bin/run_solution "$pi_server":~/.local/bin/
