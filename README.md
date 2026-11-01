# System-architecture
## System architecture & Instruction for deploying ##

The project includes a container with two images:
| Image     | Usage |
| --------- | ------------------------ |
| `traefik` | Used as the proxy server |
| `nginx`   | Used as the web server   |

## Docker network ##
Name of the network for containers' called **front_net** with bridge mode.
Only exposed ports are 80 for web and 8080 for proxy only. Web server is isolated. 

Subnet: **192.168.20.0/24**

## Using the python script ##
run command line as shown below to see available containers:
```shell
$ python3 manage.py list

traefik_proxy_server
    |__Running: False
    |__/home/user/Documents/Projects/Docker/web_app/docker-compose.yml

web_server
    |__Running: False
    |__/home/user/Documents/Projects/Docker/web_app/docker-compose.yml
```

You can proceed with corresponding operations as shown below.
> Running one container causes to run all two of them as they are dependent upon each other.
> See the docker-compose.yml file for more information.

| Subcommand      | Meaning | 
| ------------    | ------------------------------------------------------------ | 
| `version`       |   Get current version of the program.   					           |
| `start_all`     |   Run all containers sequentially.      					           |
| `list`          |   List all available containers.        			               |
| `stop`          |   Stop a container. 				      					                 |
| `rm`            |   Remove a container.				      					                 |
| `rm_all`        |   Remove all containers.			      					      	       |
| `stop_all`      |   Stop all containers.				  					                   | 
| `start`         |   Start a container. 				      					                 |	  
| `status`        |   Check the status of a container.      					           |
| `info`          |   Display essential information about a container, including [State, Network, Platform, Mounts] |                         |

> Current version of the script is v1.3
