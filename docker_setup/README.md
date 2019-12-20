# REopt Lite Docker Container Setup

## Prerequisites
This repo builds a container hosting the **REopt Lite API**. You will need Docker already installed on your machine. For install instructions, please refer to [https://docs.docker.com/v17.09/engine/installation/](https://docs.docker.com/v17.09/engine/installation/?target="_blank") .

Also note, the **REopt Lite API** is a memory intensive application. In Docker **Preferences**, under the **Advanced** settings tab increase the **Memory** as much as you can before running this server.

## Installation
To run the **REopt Lite API** you need to (1) build a container to get all the software loaded onto the container, then (2) run the container. Note there are some additional licensing steps if Xpress is used as the optimization solver. 

### XPRESS USERS

You will need to unzip the linux Xpress installation files to a folder ```solver_install_files\xpress_files``` inside the ```docker_setup```  folder before building your container. You should have files like:
- install.sh			
- xp8.0.4_linux_x86_64.tar.gz
- kalis_license.txt		
- version.txt

#### Steps
1. Once Docker is installed and running, from the _docker_setup_ folder as the working directory in a terminal window, use the following to build the image:
	```
	$ cd docker_setup
	$ docker build -t reopt:test  --build-arg github_username='<GITHUB USERNAME>' --build-arg github_password='<GITHUB PASSWORD>' --build-arg solver='<SOLVER>' .
	```
	*Note* : The . at the end is not a typo and needs to be included preceded by a space. 

	*Also* :  You will need to replace your \<GITHUB USERNAME> and \<GITHUB PASSWORD> above with your github login credentials in a [web encoded string](https://www.w3schools.com/tags/ref_urlencode.asp). For example, if your password contains a '!' replace it with '%21'. 
	Furthermore, replace the \<SOLVER> text with your solver of choice. Currently, the solver set is limited to the following: 
	- xpress
	- glpk
	 

	Be prepared for the build to take more than 20 minutes to complete...


2. Once the build has completed, move to this repository as the working directory, then create a ```docker_share``` folder then place your ```keys.py``` file in this folder. ```keys.py``` contains your API key credentials for developer.nrel.gov and other services prior to running the container.

	```
	$ cd ../
	$ mkdir docker_share
	$ cp <path to keys.py> docker_share/keys.py
	``` 

3. Now, to run the container, from the `reopt_api` directory as the working directory in a terminal window, activate the docker container with:

	```
	$ docker run -v "$(pwd)/docker_share:/share" -p 8001:8000  --restart always --name reoptcontainer --mount source=reoptdb,target=/var/lib/postgresql/9.5/main reopt:test
	```
	_Note :_ We mount the _reoptdb_ volume to the  ```/var/lib/postgresql/9.5/main``` folder such that data will persist each time the container is stopped or restarted. Exclude this mounting parameter `--mount source=reoptdb,target=/var/lib/postgresql/9.5/main` to reduce container size and have the database cleared each time the container is stopped or restarted.

4. The API will run in the terminal window in which it is activated and you'll see startup tasks print to the console. (Xpress Solver Users: See below for license activation). Wait until no new lines have printed to start using the API. 

	With the container now running you can sumbit jobs to the API at	```	localhost:8001/v1/job/```

### Xpress Solver Licensing

If you choose 'xpress' as your optimization solver you will need to follow a few more steps to activate your license before the API will work.
#### Additional Steps
5. In the ```docker_share``` folder you should now see a file ```license_info.txt```. Use the host_id in this file to generate a license file named ```xpauth.xpr```.

6. Copy your license file ```xpauth.xpr``` into the ```docker_share``` folder.
	```
	$ cp <path to license file> docker_share/xpauth.xpr
	```
8. Restart the container (from an alternate terminal window), then submit jobs to the API at _localhost:8001/v1/job/_
	```
	$ docker restart -t 0 reoptcontainer
	```
	_Note:_ This restart method will close the docker container running in the original terminal window, and restart the container in the background. Alternatively, you can run the following in an alternate terminal window, then restart the original terminal window with the same run command.
	```
	[alternate terminal window]$ docker stop reoptcontainer
	[original terminal window]$ docker run -v "$(pwd)/docker_share:/share" -p 8001:8000  --restart always --name reoptcontainer --mount source=reoptdb,target=/var/lib/postgresql/9.5/main reopt:test
	```

## Managing the Docker Container

#### Stop (any terminal window)
```
$ docker stop reoptcontainer
```

#### Restart (any terminal window)
```
$ docker restart -t 0 reoptcontainer
```

#### Start (terminal window with this repository as the working directory)
```
$ docker run -v "$(pwd)/docker_share:/share" -p 8001:8000  --restart always --name reoptcontainer --mount source=reoptdb,target=/var/lib/postgresql/9.5/main reopt:test
```

#### Interactive Commands on Container 

You can interactively run commands in the docker container with:

```
docker exec -it reoptcontainer /bin/bash
```

#### Cleaning up Dockerfiles

You can clear non-running images,  containers and build caches with:

```
docker system prune
```


#### Accessing file directory

You can explore the file directory inside the docker container with command line functions such as:

```
docker exec reoptcontainer ls
```
