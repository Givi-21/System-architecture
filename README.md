# System-architecture
## System architecture & Instruction for deploying ##

The project includes a container with two images:
| Image |   | Usage |
| ---------- |   | ---------------------------|
| `traefik` | Used as the proxy server |
| `nginx`   | Used as the web server   |

## Docker network ##
The name of the network is **front_net** for docker containers.
Only exposed ports are 80 and 8080 for traefik image only. Web server is isolated. 
> 80 for web and 8080 for traefik default local diagram page.

subnet **192.168.20.0/24**

# Using the python script

Can you make a diagram for readme in github?

| Subcommand |  | Meaning | 
| ------------- | -------------------------------------------------------------     				   | 
| `version`       |   Get current version of the program.   					   | 
| `start_all`     |   Run all containers sequentially.      					   | 
| `list`          |   List all available containers.        			           | 
| `stop`         |   Stop a container. 				      					   | 
| `rm`            |   Remove a container.				      					   | 
| `rm_all`        |   Remove all containers.			      					   |  	
| `stop_all`      |   Stop all containers.				  					   | 
| `start`         |   Start a container. 				      					   | 	
| `status`        |   Check the status of a container.      					   | 
| `info`          |   Display essential information about a container, including |  [State, Network, Platform, Mounts]

> Current version of the script is v1.3
