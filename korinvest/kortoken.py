import requests
import os
import requests
from dotenv import load_dotenv, find_dotenv

# --- 환경변수 로드 ---
load_dotenv(find_dotenv())

# --- API 키 및 토큰 설정 (환경변수에서 로드) ---
APP_KEY = os.environ.get('KOREA_INVEST_APP_KEY')
APP_SECRET = os.environ.get('KOREA_INVEST_APP_SECRET')

if not all([APP_KEY, APP_SECRET]):
    raise ValueError('필수 환경변수가 설정되지 않았습니다: KOREA_INVEST_APP_KEY, KOREA_INVEST_APP_SECRET')

url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
headers = {
    "Content-Type": "application/json; charset=UTF-8"
}
data = {
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
}

print(data)

response = requests.post(url, headers=headers, json=data)
token_json = response.json()
print(token_json)

# access_token 추출
#access_token = token_json['access_token']
#print("Access Token:", access_token)