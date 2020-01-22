# Docker documentation for REopt Lite API
After cloning the API, you must set up your keys.py.
Within the directory that you cloned the REopt API is a file called `keys.py.template`. First, copy `keys.py.template` to `keys.py` (in the same directory.
Then, [get a NREL Developer API key](https://developer.nrel.gov/signup/) and replace the `DEMO-KEY` value within `keys.py` with your API key.


Once you have your keys.py set up:
1. Install docker-compose
2. From the top directory:
```
docker-compose up
```
3. Make POST's and GET's using `0.0.0.0:8000/v1/` as the root URL

## Changing Solver
By default the solver is set to Cbc (because it does not require a license and therefore builds without any additional steps).
If you would like to use another solver we have set up Dockerfile's for SCIP and Xpress, but these (and other solvers) require extra steps, which are described below.

### SCIP
To use [SCIP](https://scip.zib.de/) you will need to download SCIPOptSuite-6.0.2-Linux.deb (or another version if you wish, but you will have to modify the Dockerfile.scip).
Place SCIPOptSuite-6.0.2-Linux.deb in the "solver" directory before running `docker-compose up`.
Note: if you have previously run `docker-compose up` with another solver then you will need to add the `--build` option.

Additionally, in docker-compose.yml, under the `celery` service, change the `dockerfile` setting to `Dockerfile.scip`
and change the `environment` variable for `SOLVER` within the `celery` and `reopt` services to `scip`.

Note: The Dockerfile.scip starts from the Ubuntu 18.04 image instead of the Python3 image because SCIP is not compatible for Jessie Debian 8 (which is the OS for the Python3 image).

### Xpress
Similar to changing to the SCIP solver, under the `celery` service, change the `dockerfile` setting to `Dockerfile.xpress`
and change the `environment` variable for `SOLVER` within the `celery` and `reopt` services to `xpress`.

Next, obtain the install files from FICO Xpress and put the following files into the project "solver" directory:
- install.sh
- xp8.0.4_linux_x86_64.tar.gz
- xpauth.xpr (see "Xpress license" section below)

### Xpress license
There is an extra step to get your Xpress license:
- After running `docker-compose up` you need to `docker exec -it celery bash` in order to run the Xpress Host ID tool.
- Once you are logged into a bash terminal within the celery container (via `docker exec -it celery bash`), change your directory via
```
cd /opt/xpressmp/bin/
```
- Then
```
./xphostid
```
- Copy the output of the Xpress Host ID tool and send to your Xpress license manager or user the online Xpress tool to get your `xpauth.xpr` file
- Finally, place your `xpauth.xpr` file in the `solver` directory and rebuild

NOTE: You may have issues with your Xpress license being associated with a particular MAC address. The license should be tied to the MAC address of the `celery` service image.
You can set the MAC address of the `celery` service in the docker-compose.yml file by adding the option:
```
mac_address: <image-mac-adress>
```


### Interactive Commands on Container 
#### to check if all the containers are running as expected, run the following command:
docker ps
You can interactively run commands in a docker container with:

```
docker exec -it <container-name> /bin/bash
```
where container names can be found via `docker ps`. For more see the [Docker documentation](https://docs.docker.com/).

For instructions on running tests when logged into the `celery` container see [Testing the REopt API](https://github.com/NREL/reopt_api/wiki/Testing-the-REopt-API).


### FAQ

#### address already in use
If you are already running PostgreSQL or Redis when you start the docker containers then you may get a conflict with the ports that PostgreSQL and Redis use. To fix this you can either shut down your PostgreSQL and/or Redis servers or change the port numbers in the docker-compose.yml file. For more on ports see the [Docker documentation](https://docs.docker.com/).
