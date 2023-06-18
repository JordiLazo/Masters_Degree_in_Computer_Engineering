#!/bin/bash

ifconfig tap0 11.0.0.1/24
ifconfig tap1 12.0.0.1/24

sudo route add -net 13.0.0.0/8 11.0.0.2
sudo route delete 13.0.0.2 11.0.0.2
route add -host 13.0.0.2 12.0.0.2


