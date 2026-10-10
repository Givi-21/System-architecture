# System-architecture
System architecture & Instruction for deploying

The project includes docker containers and one script for managing them all together.

Containers:
  - DNS Server(internetsystemsconsortium/bind9:9.18)
  
**One docker compose file**
  - Web Server(Alpine, Nginx)
  - Reverse proxy(Alpine, Nginx)

  Network:
  > name - front_net
> 
  > subnet - 192.168.20.0/24

DNS server binds the Domain Name to the proxy server. 
Web server by itself is completely isolated for security.

for better security, you can change the owner of ./dsn_server/bind9 folder:
sudo chown -R root:bind ./bind9
sudo chmod -R 644 ./bind9

Using the script. 
script version - v1.1

run: 
> manage.py --help to see available flags for additional functionalities.

flags:
  - all: Run all containers.
  - start: start a specific container(requires container name).
  - stop: stop a specific container(requires container name).
  - status: see if a container is active(requires container name).
  - stop_all: Stop all containers gracefully.
  - list: list all available containers with the path of their compose files.

> Note, if you use Windows for testing this project, you must have WSL2 installed alongside docker. WSL2 is logically on an isolated network, which
   makes it natively diffucult to optimize it for this specific OS. you cannot get web page via curl or a web browser by domain. For resolving this issue, you can make custom domain for the web server in
   **C:\Windows\System32\drivers\etc\hosts** as specified below:

	 127.0.0.1   homelab.lan.
   for additional testing you can access a container's terminal via **docker exec -ti <container name> sh**.

