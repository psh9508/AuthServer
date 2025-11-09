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



## CI/CD

<img src="https://github.com/user-attachments/assets/3eac1b98-1265-454b-9463-1e1a15681cce" />

1. When code is pushed to the branches starting with **'release/'**, upload all the source code to `S3` via `github actions`.

2. When a file named **'source.zip'** is created in a specific bucket, `EventBridge` is triggered, which triggers `CodePipeline`. `CodePipeline` will trigger `CodeBuild` and `CodeDeploy` sequentially.

3. `CodeBuild` opens the file named **'source.zip'** then makes a `Docker image`.

4. Uploads it to `ECR`.

5. When `CodeBuild` ends, `CodePipeline` starts to run `CodeDeploy`, which deploys the `Docker image` to `ECS`. It uses an artifact created by `CodeBuild`, which contains the information about the image to be deployed.

---
