### 한국어 버전은 아래에서 확인할 수 있습니다.

[한국어 버전](./docs/README.ko.md)

# Auth Server

When it gets a login request, it verifies the login information and returns a `JWT`.

## Dependency
- Postgres  
  - I'm using this DB in my company, and since it's a free open-source project, I think it would be good to use it in this project.
- Redis
  - The datastore that manages JWT refresh tokens.
- Docker
  - To easily connect various dependencies.

## How to start this project

1. run docker-compose

    ``` bash
    docker-compose --env-file .env -f dependency/docker-compose.yml up -d
    ```

2. run this project

    ``` bash
    uv run main.py
    ```
test