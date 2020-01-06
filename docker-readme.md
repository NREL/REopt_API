# Docker documentation for REopt Lite API
1. Install docker-compose
2. From the top directory:
```
docker-compose-up
```
3. Make POST's and GET's using `0.0.0.0:8000/v1/` as the root URL

## Changing Solver
In docker-compose.yml, under the `celery` service, change the `dockerfile` setting to one of:
- Dockerfile.xpress
- Dockerfile.cbc
2. and change the `environment` variable for `SOLVER` within the `celery` and `reopt` services to the corresponding solver:
- `xpress`
- `cbc`

## Xpress license
There is an extra step to get your Xpress license:
- After running `docker-compose up` you need to `docker exec -it celery bash` in order to run the Xpress Host ID tool.
- Once you are logged into a bash terminal within the celery container (via `docker exec -it celery bash`), change your directory via
```
cd cd /opt/xpressmp/bin/
```
- Then
```
./xphostid
```
- Copy the output of the Xpress Host ID tool and send to your Xpress license manager or user the online Xpress tool to get your `xpauth.xpr` file
- Finally, place your `xpauth.xpr` file in the `solver` directory
