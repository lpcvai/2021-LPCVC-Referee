#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../../
mkdir -p ~/.config/systemd/user/
cp service/lpcvc.service ~/.config/systemd/user/
systemctl daemon-reload --user
systemctl restart lpcvc.service --user
exit