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
```

## 파일 설명

파일명	설명
main.py	프로그램의 전체 실행 흐름을 담당
config.py	API 키, 계좌 정보, 종목코드 등 설정값 관리
auth.py	한국투자증권 API 접근 토큰 발급
kis_client.py	시세 조회, 호가 조회, 주문 요청 등 API 통신 담당
strategy.py	매수/매도 조건 판단
trader.py	전략 결과에 따른 실제 주문 실행
logger.py	실행 결과 및 주문 로그 기록
.env.example	환경변수 예시 파일
requirements.txt	실행에 필요한 Python 패키지 목록

# Samsung Auto Trader

한국투자증권 Open API를 이용하여 삼성전자(005930)를 대상으로 자동매매 흐름을 구현한 프로젝트입니다.

본 프로젝트는 실제 수익 창출보다는 **증권사 API를 활용한 자동매매 시스템의 기본 구조를 이해하고 구현하는 것**을 목적으로 합니다.

---

## 1. 프로젝트 개요

이 프로젝트는 삼성전자 주식을 대상으로 다음과 같은 자동매매 과정을 구현합니다.

1. 한국투자증권 Open API 접근 토큰 발급
2. 삼성전자 현재가 또는 호가 정보 조회
3. 매매 조건 판단
4. 매수 또는 매도 주문 요청
5. 주문 결과 및 실행 로그 기록

---

## 2. 개발 목적

본 프로젝트의 목적은 단순한 매매 전략 구현이 아니라, 실제 금융 API를 활용하여 자동매매 시스템의 전체 흐름을 직접 구현하는 것입니다.

주요 학습 목표는 다음과 같습니다.

* REST API 기반 증권사 API 호출 구조 이해
* 접근 토큰 발급 및 인증 헤더 구성
* 주식 현재가 및 호가 정보 조회
* 조건에 따른 매수/매도 주문 실행
* 주문 결과 로그 기록
* 자동매매 프로그램의 모듈화 구조 설계

---

## 3. 프로젝트 구조

```text
samsung_auto_trader/
├── README.md
├── .env.example
├── requirements.txt
├── main.py
├── config.py
├── auth.py
├── kis_client.py
├── strategy.py
├── trader.py
└── logger.py
```

---

## 4. 파일 설명

| 파일명                | 설명                              |
| ------------------ | ------------------------------- |
| `main.py`          | 프로그램의 전체 실행 흐름을 담당              |
| `config.py`        | API 키, 계좌 정보, 종목코드 등 설정값 관리     |
| `auth.py`          | 한국투자증권 API 접근 토큰 발급             |
| `kis_client.py`    | 시세 조회, 호가 조회, 주문 요청 등 API 통신 담당 |
| `strategy.py`      | 매수/매도 조건 판단                     |
| `trader.py`        | 전략 결과에 따른 실제 주문 실행              |
| `logger.py`        | 실행 결과 및 주문 로그 기록                |
| `.env.example`     | 환경변수 예시 파일                      |
| `requirements.txt` | 실행에 필요한 Python 패키지 목록           |

---

## 5. 실행 환경

* Python 3.9 이상
* Windows PowerShell 또는 VS Code Terminal
* 한국투자증권 Open API 계정
* 모의투자 또는 실제투자 계좌

---

## 6. 설치 및 실행 방법

### 6.1 저장소 클론

```bash
git clone https://github.com/본인아이디/레포지토리이름.git
cd 레포지토리이름
```

### 6.2 가상환경 생성

```bash
python -m venv .venv
```

### 6.3 가상환경 실행

Windows PowerShell 기준:

```bash
.venv\Scripts\Activate.ps1
```

### 6.4 패키지 설치

```bash
pip install -r requirements.txt
```

### 6.5 환경변수 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성합니다.

```env
APP_KEY=your_app_key
APP_SECRET=your_app_secret
ACCOUNT_NO=your_account_number
PRODUCT_CODE=01
BASE_URL=your_base_url
```

주의: `.env` 파일에는 개인 API 키와 계좌 정보가 포함되므로 GitHub에 업로드하지 않습니다.

---

## 7. 실행 방법

```bash
python main.py
```

프로그램을 실행하면 다음 순서로 작동합니다.

1. API 접근 토큰 발급
2. 삼성전자 시세 또는 호가 조회
3. 전략 조건 확인
4. 주문 요청
5. 실행 결과 출력 및 로그 저장

---

## 8. 매매 전략

본 프로젝트에서는 복잡한 가격 예측 모델이 아니라, API 연동과 주문 흐름 검증을 위한 단순 전략을 사용했습니다.

기본 전략은 다음과 같습니다.

* 삼성전자(005930)의 현재가 또는 호가 정보를 조회합니다.
* 설정한 조건을 만족하면 매수 또는 매도 주문을 요청합니다.
* 주문 결과를 로그로 저장합니다.

이 전략은 실제 투자 수익을 보장하기 위한 것이 아니라, 자동매매 시스템의 기본 작동 방식을 확인하기 위한 학습용 전략입니다.

---

## 9. 실제 거래 결과

교수님의 요구사항에 따라 실제 주문 또는 체결 내역을 준비했습니다.

개인정보 보호를 위해 다음 정보는 제거하거나 가렸습니다.

* 계좌번호
* API Key
* API Secret
* 접근 토큰
* 주문번호 일부
* 개인 식별 정보

제출 자료에는 다음 정보가 포함됩니다.

* 주문 일시
* 종목명 및 종목코드
* 매수/매도 구분
* 주문 가격
* 주문 수량
* 체결 여부
* 실행 로그 또는 주문 결과 화면

---

## 10. 주요 코드 흐름

```text
main.py
→ auth.py에서 접근 토큰 발급
→ kis_client.py에서 현재가 또는 호가 조회
→ strategy.py에서 매매 조건 판단
→ trader.py에서 주문 실행
→ logger.py에서 결과 기록
```

---

## 11. 한계점

현재 프로젝트는 학습 목적의 자동매매 시스템이므로 다음과 같은 한계가 있습니다.

* 복잡한 수익률 예측 모델은 포함하지 않았습니다.
* 수수료와 세금이 전략에 정교하게 반영되지 않았습니다.
* 주문 실패, 네트워크 오류, 중복 주문 방지 로직이 제한적입니다.
* 실제 투자에 사용하기 위해서는 손절, 익절, 포지션 관리 등 리스크 관리 기능이 추가로 필요합니다.

---

## 12. 배운 점

이 프로젝트를 통해 단순히 매매 전략을 작성하는 것뿐만 아니라, 실제 금융 API를 사용하는 과정에서 인증, 요청 헤더, 주문 파라미터, 로그 기록, 예외 처리 등이 중요하다는 것을 배웠습니다.

또한 자동매매 시스템에서는 전략 자체뿐만 아니라 안정적인 실행 구조와 리스크 관리가 매우 중요하다는 점을 확인했습니다.

---

## 13. 주의사항

본 프로젝트는 학습 및 과제 제출 목적의 프로젝트입니다.
실제 투자에 사용할 경우 손실이 발생할 수 있으며, 투자 판단과 책임은 사용자 본인에게 있습니다.
