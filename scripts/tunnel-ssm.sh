#!/bin/bash

# Dev-local SSM Port Forwarding Script
# AWS SSM을 통한 DB 포트 포워딩

set -e

# AWS 설정
PROFILE="cam2025-superpower"
REGION="ap-northeast-2"
BASTION_ID="i-047166114e74af147"

# DB 엔드포인트
SAURON_ENDPOINT="mimircdkstack-saurondbinstanceff0fa985-ri5kb59hnvc3.c5gqoi66wwnc.ap-northeast-2.rds.amazonaws.com"
AUTH_ENDPOINT="mimircdkstack-authdbinstance93a2d0c2-gpuhtst1x0xy.c5gqoi66wwnc.ap-northeast-2.rds.amazonaws.com"
REDIS_ENDPOINT="authcache.qvcnpj.ng.0001.apn2.cache.amazonaws.com"

# 로컬 포트
SAURON_LOCAL_PORT=5432
AUTH_LOCAL_PORT=5433
REDIS_LOCAL_PORT=6380

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# PID 저장용
PIDS=()

cleanup() {
    echo -e "\n${YELLOW}터널 종료 중...${NC}"
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    echo -e "${GREEN}모든 터널이 종료되었습니다.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# SSO 로그인 확인
check_sso() {
    echo -e "${BLUE}SSO 인증 확인 중...${NC}"
    if ! aws sts get-caller-identity --profile "$PROFILE" &>/dev/null; then
        echo -e "${YELLOW}SSO 로그인이 필요합니다.${NC}"
        aws sso login --profile "$PROFILE"
    fi
    echo -e "${GREEN}SSO 인증 완료${NC}"
}

# 포트 사용 여부 확인
check_port() {
    local port=$1
    if lsof -i ":$port" &>/dev/null; then
        echo -e "${RED}포트 $port가 이미 사용 중입니다.${NC}"
        return 1
    fi
    return 0
}

# SSM 세션 시작
start_tunnel() {
    local name=$1
    local host=$2
    local remote_port=$3
    local local_port=$4

    echo -e "${YELLOW}$name 터널 시작 중...${NC}"
    echo "  localhost:$local_port -> $host:$remote_port"

    aws ssm start-session \
        --target "$BASTION_ID" \
        --document-name AWS-StartPortForwardingSessionToRemoteHost \
        --parameters "{\"host\":[\"$host\"],\"portNumber\":[\"$remote_port\"],\"localPortNumber\":[\"$local_port\"]}" \
        --profile "$PROFILE" \
        --region "$REGION" &>/dev/null &

    PIDS+=($!)
    sleep 2
}

# 메인 실행
main() {
    echo -e "${GREEN}=== Dev-local SSM 포트 포워딩 ===${NC}"
    echo ""

    # SSO 확인
    check_sso
    echo ""

    # 포트 확인
    for port in $SAURON_LOCAL_PORT $AUTH_LOCAL_PORT $REDIS_LOCAL_PORT; do
        if ! check_port "$port"; then
            echo -e "${RED}종료합니다. 해당 포트를 사용 중인 프로세스를 종료해주세요.${NC}"
            exit 1
        fi
    done

    # 터널 시작
    start_tunnel "SauronDB" "$SAURON_ENDPOINT" "5432" "$SAURON_LOCAL_PORT"
    start_tunnel "AuthDB" "$AUTH_ENDPOINT" "5432" "$AUTH_LOCAL_PORT"
    start_tunnel "Redis" "$REDIS_ENDPOINT" "6379" "$REDIS_LOCAL_PORT"

    echo ""
    echo -e "${GREEN}=== 터널 활성화 완료 ===${NC}"
    echo ""
    echo -e "  SauronDB:   ${BLUE}localhost:$SAURON_LOCAL_PORT${NC}"
    echo -e "  AuthDB:     ${BLUE}localhost:$AUTH_LOCAL_PORT${NC}"
    echo -e "  Redis:      ${BLUE}localhost:$REDIS_LOCAL_PORT${NC}"
    echo ""
    echo -e "${YELLOW}앱 실행: ENV=dev-local uv run main.py${NC}"
    echo ""
    echo "Ctrl+C로 터널을 종료합니다."

    # 터널 유지
    wait
}

main "$@"
