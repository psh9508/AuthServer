# Auth Server

로그인 요청이 들어오면 로그인 정보를 확인하고 `JWT`를 리턴한다.

## Dependency
- Postgres  
  - 현재 현업에서 사용 중인 DB로 무료 오픈소스로 현재 프로젝트에 사용하기 적합하다고 판단
- Redis
  - `JWT`의 Refresh token을 관리하기 위한 저장소
- Docker
  - 다양한 의존성을 쉽게 연결하기 위해서 사용

## How to start this project

1. docker-compose 파일 실행

    ``` bash
    docker-compose --env-file .env -f dependency/docker-compose.yml up -d
    ```

2. project 실행

    ``` bash
    uv run main.py
    ```



## CI/CD

<img src="https://github.com/user-attachments/assets/3eac1b98-1265-454b-9463-1e1a15681cce" />

### 자세히

CI/CD에 대한 자세한 설명을 원하시는 사람이 있다면 [클릭해서 자세히 보기](https://github.com/psh9508/AuthServer/wiki/CICD).

### 요약

1. **'release/'** 로 시작하는 브랜치에 코드가 푸시되면, `GitHub Actions`를 통해 모든 소스 코드를 `S3`에 업로드한다.

2. 특정 버킷에 **'source.zip'** 파일이 생성되면 `EventBridge`가 트리거되어 `CodePipeline`이 실행된다. `CodePipeline`은 순차적으로 `CodeBuild`와 `CodeDeploy`를 실행한다.

3. `CodeBuild`는 **source.zip** 파일을 열어 Docker 이미지를 생성한다.

4. 생성된 이미지를 `ECR`에 업로드한다.

5. `CodeBuild`가 끝나면 `CodePipeline`은 `CodeDeploy`를 실행하여 Docker 이미지를 `ECS`에 배포한다. 이때 `CodeBuild`에서 생성된 아티팩트를 사용하며, 그 안에는 배포할 이미지에 대한 정보가 포함되어 있다.