# Samsung Auto Trader

한국투자증권 Open API 모의투자 환경을 활용한 삼성전자(005930) 자동매매 시스템입니다.

## Project Goal

이 프로젝트는 실제 투자 수익을 목적으로 하는 프로그램이 아니라, 한국투자증권 Open API를 사용하여 다음 과정을 학습하고 구현하는 교육용 프로젝트입니다.

- REST API 인증
- 접근토큰 캐싱
- 현재가 조회
- 계좌 잔고 조회
- 모의투자 주문 요청
- 주문 후 보유 수량 확인
- 단순 매매 전략 구현
- 거래 가능 시간 제한
- 로그 기록

## Target

- Stock: Samsung Electronics
- Code: 005930
- Environment: Mock trading only
- API style: REST polling only
- WebSocket: Not used

## Folder Structure

```text
samsung_auto_trader/
├── main.py
├── config.py
├── auth.py
├── kis_client.py
├── strategy.py
├── trader.py
├── logger.py
├── requirements.txt
├── README.md
└── .env.example