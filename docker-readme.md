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
In docker-compose.yml, under the `celery` service, change the `dockerfile` setting to one of:
- Dockerfile.xpress
- Dockerfile.cbc
2. and change the `environment` variable for `SOLVER` within the `celery` and `reopt` services to the corresponding solver:
- `xpress`
- `cbc`

## Xpress solver
If you are using FICO Xpress as the solver, then you must put the following files into the project `solver` directory:
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
- Finally, place your `xpauth.xpr` file in the `solver` directory

NOTE: You may have issues with your Xpress license being associated with a particular MAC address.
If so you can set the MAC address of the `celery` service in the docker-compose.yml file by adding the option:
```
mac_address: <image-mac-adress>
```


#### Interactive Commands on Container 

You can interactively run commands in a docker container with:

```
docker exec -it <container-name> /bin/bash
```
where container names can be found via `docker ps`. For more see the [Docker documentation](https://docs.docker.com/).

For instructions on running tests when logged into the `celery` container see [Testing the REopt API](https://github.com/NREL/reopt_api/wiki/Testing-the-REopt-API).