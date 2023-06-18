# Commands for configuring the network topology
1. [MacOS](#macos)
2. [Ubuntu](#ubuntu)
3. [Cisco](#cisco)


## MacOS
### 1- How to create taps
```
write here @Alejandro
```
### 2- Add IP address to the tap
```
write here @Alejandro
```
```
write here @Alejandro
```
### 3- Configure the tap routes
```
write here @Alejandro
```
```
write here @Alejandro
```
## Ubuntu
### 1- How to create taps
```
sudo ip tuntap add tap0 mode tap
```
```
sudo ip tuntap add tap1 mode tap
```
### 2- Add IP address to the tap
```
sudo ifconfig tap0 11.0.0.1/24
```
```
sudo ifconfig tap1 12.0.0.1/24
```
### 3- Configure the tap routes
```
sudo ip route add 11.0.0.1/24 via 11.0.0.2 dev tap0
```
```
sudo ip route add 12.0.0.1/24 via 12.0.0.2 dev tap1
```
### 4- Check is the taps are created correctly
```
ifconfig -a
```
## Cisco
### 1- Configure router R1:
```
configure terminal
```
```
interface FastEthernet 0/0
ip address 11.0.0.2 255.255.255.0
no shutdown

interface FastEthernet 0/1
ip address 12.0.0.2 255.255.255.0
no shutdown
```
```
interface Serial 2/0
ip address 172.16.0.1/2 ??????(not configured)
no shutdown
```
```
copy running-config startup-config
```
### 2- Configure router R2:
```
configure terminal
```
```
interface FastEthernet 0/0
ip address 13.0.0.2 255.255.255.0
no shutdown

interface FastEthernet 0/1
ip address 14.0.0.2 255.255.255.0
no shutdown

interface Serial 2/0
ip address 172.16.0.1/2 ??????(not configured)
no shutdown
```
```
copy running-config startup-config
```
### 3- Configure router R3:
```
configure terminal
```
```
interface FastEthernet 0/0
ip address 13.0.0.1 255.255.255.0
no shutdown
```
```
copy running-config startup-config
```
### 4- Configure router R4:
```
configure terminal
```
```
interface FastEthernet 0/0
ip address 14.0.0.1 255.255.255.0
no shutdown
```
```
copy running-config startup-config
```