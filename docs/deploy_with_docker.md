
# Deploying as Docker Container

The container provides a full-fledged Python and DBT environment.

To build the container and run commands:

```bash
# get the latest image
docker pull ghcr.io/linkfish-consulting/python-dbt-stack:latest
# ... or a specific version
docker pull ghcr.io/linkfish-consulting/python-dbt-stack:v0.1.4

# create a tag, to access more conveniently
docker tag ghcr.io/linkfish-consulting/python-dbt-stack:v0.1.4 lf-py-stack

# run a command as the default non-root user (lf_admin)
docker run --rm -it lf-py-stack dbt --version
```

Usually you will need to mount data and project folders into the container via the `--volume` command:

```bash
docker run -it --rm --volume /coasti:/coasti lf-py-stack dbt --version
```

If you want to run as the root user, the usual `-u root` will not be sufficient, because we fix permissions and then drop to lf_admin.

```bash
# skip our entrypoint to run as root
docker run -it --rm -u root --entrypoint="" lf-py-stack bash
```

## Environement Variables

The Container supports the following environment variables.
Specify as e.g. `docker run -e EXTRA_GIDS=1002,1003`

- `PUID` set the user ID for lf_admin
- `GUID` set the group ID for lf_admin
- `EXTRA_GIDS` add lf_admin to extra groups, e.g. to be able to read from folder mounts owned by other users.


## Docker Compose

For a more involved setup:

```yaml
# docker-compose.yml
services:
    lf-py-stack:
        image: ghcr.io/linkfish-consulting/python-dbt-stack:latest
        # other settings, e.g.
        environment:
            - PUID: 1001
            - GUID: 1001
        volumes:
            - /coasti/data/:/coasti/data/
            - /coasti/products/haushaltplus/:/coasti/products/haushaltplus/
```

then run with
```bash
docker compose -f /path/to/docker-compose.yml run -it --rm lf-py-stack dbt --version
```

Often you will need some setup, like loading environment variables inside the container.
Then, it can be helpful to define an init command that can be reused:

```bash
INIT_CMD="set -a; source ./config/.env; set +a;"
docker run -it --rm --workdir /coasti/products/haushaltplus \
    lf-py-stack bash -c "$INIT_CMD dbt version"
```


## Building the container locally

If you have cloned the repo:

```bash
docker compose build
docker run -it --rm lf-py-stack bash
```
