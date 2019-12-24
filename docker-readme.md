# Docker documentation for REopt Lite API
1. Install docker-compose
2. From the top directory:
```
docker-compose-up
```
3. Make POST's and GET's using `0.0.0.0:8000/v1/` as the root URL

## Changing Solver
In docker-compose.yml, change the `dockerfile` setting under the `celery` service to one of:
- Dockerfile.xpress
- Dockerfile.cbc
