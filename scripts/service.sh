#!/usr/bin/env bash
mkdir -p ~/.config/systemd/user/
cp service/lpcvc.service ~/.config/systemd/user/
systemctl daemon-reload --user
systemctl restart lpcvc.service --user