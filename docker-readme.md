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
