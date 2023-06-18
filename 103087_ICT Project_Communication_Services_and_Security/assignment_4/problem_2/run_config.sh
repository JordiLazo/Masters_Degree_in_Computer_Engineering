#!/bin/bash

ifconfig tap0 11.0.0.1/24 up
ifconfig tap1 12.0.0.1/24 up

sudo route add -host 13.0.0.1 11.0.0.2
sudo route add -host 14.0.0.1 12.0.0.2
