#! /bin/bash

if [ $1 = block ]
then
  sudo iptables -A INPUT -s 128.46.75.108 -j ACCEPT
  sudo iptables -A OUTPUT -d 128.46.75.108 -j ACCEPT
  sudo iptables -A INPUT -s 128.46.75.200 -j ACCEPT
  sudo iptables -A OUTPUT -d 128.46.75.200 -j ACCEPT

  sudo iptables -P INPUT DROP
  sudo iptables -P OUTPUT DROP
elif [ $1 = allow ]
then
  sudo iptables -P INPUT ACCEPT
  sudo iptables -P OUTPUT ACCEPT
else
  echo "Please enter 'block' to disable all connections except for meter and server or 'allow' to allow all connections"
fi
