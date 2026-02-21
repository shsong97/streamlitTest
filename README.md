# Project 설명
- streamlit 을 사용하여 데이터 시각화를 연습한다.
- dataframe을 다루는 방법을 학습한다.

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

