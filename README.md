
# Python 데이터 분석/시각화/주식 자동화 프로젝트

이 프로젝트는 **Streamlit** 기반의 웹앱과 다양한 데이터 분석, 주식 자동화, 차트 시각화, 인증 기능, 샘플 데이터 분석 예제 등을 포함합니다. 한국투자증권 OpenAPI, KOSIS(통계청) API, yfinance, FinanceDataReader 등 다양한 외부 데이터 소스를 활용합니다.

## 주요 폴더 및 파일 구조

- **streamlit_app.py**: Streamlit 기반 메인 앱. 여러 페이지(차트, 인증, 샘플 등)로 구성된 대시보드.
- **korinvest/**: 한국투자증권 OpenAPI 연동, 토큰 발급, 주식 시세/랭킹 조회, 토큰 자동 갱신 등 주식 자동화 핵심 모듈.
	- korinvest.py: OpenAPI 토큰 발급 및 랭킹 조회
	- korquery.py: 토큰 자동 갱신, 개별 종목 시세 조회
	- kortoken.py: 토큰 발급 예제
	- koreanpo.py: KOSIS API(통계청) 연동, 인구 데이터 시각화
- **pages/**: Streamlit 페이지별 UI/기능 구현
	- chartsearch.py: 네이버/야후 주식 차트(1개월) 검색 및 시각화
	- chart6mo.py: 주요 종목 6개월 차트, 네이버 금융 연동
	- loginauth.py: 파일 기반 회원가입/로그인 인증(암호화 저장)
	- users.json: 회원 정보 저장 파일
- **sample/**: 데이터 분석/시각화/백테스트/샘플 코드
	- korbacktest.py: 주식 보조지표(RSI, 볼린저밴드, MACD 등) 기반 백테스트 및 신호 스캔, 시각화
	- korstockraise.py: 반도체 등 테마주 급등주 스크리닝
	- irisdata.py: scikit-learn iris 데이터셋 분석/필터링/시각화 예제
	- pdsample.py: pandas DataFrame/차트/컴포넌트 샘플
	- streamlittest.py: Streamlit 위젯/차트/탭/메트릭 등 다양한 UI 예제
- **util/**: 공통 유틸리티
	- plotfont.py: 한글 폰트 자동 적용 함수
- **static/**: 폰트 등 정적 파일

## 주요 기능 요약

- **주식 자동화/데이터 수집**
	- 한국투자증권 OpenAPI 연동(토큰 발급, 랭킹/시세 조회, 토큰 자동 갱신)
	- KOSIS(통계청) API 연동(인구 등 공공데이터)
	- yfinance, FinanceDataReader 등으로 국내외 주가 데이터 수집
- **Streamlit 기반 대시보드/시각화**
	- 종목 콤보박스(한글명/심볼) 선택 → 실시간 차트/백테스트/시각화 (pages/charvisual.py)
	- 종목 선택 시 _prepare_indicator_df, run_backtest_and_visualize 자동 호출, Streamlit에서 바로 차트/결과 확인
	- 종목 차트 검색, 6개월 차트, iris 데이터, pandas 샘플, 로그인 인증 등 다양한 페이지 제공
	- 파일 기반 회원가입/로그인(암호화 저장)
- **PyQt 기반 종목 검색/시각화**
	- pyqt_stock_scanner.py: 종목코드/명/초성 자동완성, 단일검색, Visual 버튼(단일/테이블행별), 테이블 내 네이버금융 HTML 링크, 선택시 배경색/링크색 커스텀 등 다양한 UI 기능
	- Visual 버튼 클릭 시 run_backtest_and_visualize로 바로 차트 시각화
	- 테이블 내 각 행별 Visual 버튼, HTMLDelegate로 링크 컬럼만 별도 스타일 적용
	- 선택 배경색 회색, 링크 컬럼만 별도 색상 적용 등 UI 개선
- **주식 백테스트/신호 스캔**
	- RSI, 볼린저밴드, MACD, StochRSI 등 다양한 보조지표 기반 신호 탐지 및 시각화
	- 테마주(반도체 등) 급등주 조건 스크리닝
- **데이터 분석/시각화 예제**
	- pandas, scikit-learn, matplotlib, plotly 등 다양한 라이브러리 활용
	- Streamlit의 다양한 컴포넌트/차트/탭/메트릭 시연

## 설치 및 실행

### 전체 패키지 설치
```bash
pip install -r requirements.txt
```

### 주요 패키지 개별 설치 예시
```bash
pip install streamlit scikit-learn yfinance FinanceDataReader pandas matplotlib
```

### requirements.txt 생성
```bash
pip freeze > requirements.txt
```

### Streamlit 앱 실행
```bash
streamlit run streamlit_app.py
```

## 예시 화면/실행 흐름

1. `streamlit run streamlit_app.py` 실행 → 대시보드 접속
2. 좌측 메뉴에서 차트, 인증, 샘플 등 다양한 페이지 탐색
3. 주식 데이터/공공데이터 실시간 조회 및 시각화, 백테스트, 조건검색 등 활용

## 참고/문서

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [한국투자증권 OpenAPI](https://apiportal.koreainvestment.com/)
- [KOSIS 통계청 OpenAPI](https://kosis.kr/openapi/)
- [FinanceDataReader](https://financedata.github.io/posts/finance-data-reader-users-guide.html)


## 설치
### streamlit 참고 사이트
🐶 Streamlit site : <https://streamlit.io>

### 전체 설치
```python
pip install -r requirements.txt
```

### 개별 설치
```python
pip install streamlit
pip install scikit-learn
```

### requirements.txt 생성은 참고
```python
pip freeze > requirements.txt
```
## 화면 개발
- streamlit을 이용하여 화면 개발 방법을 확인한다.

### UI 화면 작성

### 로그인/로그아웃
* auth 활용

### 그래프 그리기

### 데이터를 저장하고 불러오기
* 데이터베이스 사용 방법
* sqlite 사용
* ms sql 사용

## Dataset 활용

### Yahoo finance 에서 dataset을 다운 받기

```python
import streamlit as st
import yfinance as yf

# 두 종목 데이터 다운로드
symbols = ['005930.KS', '000660.KS']
lables = ['삼성전자', 'SK하이닉스']

# 6개월 자료 다운로드
data = yf.download(symbols, period='6mo', auto_adjust=True)["Close"]
```


## 데이터 분석 활용하기

### 상관관계 분석

### 향후 데이터 예측

### api를 이용한 거래

### 한국투자 api 활용

