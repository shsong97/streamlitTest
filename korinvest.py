import requests

# 한국투자증권 OpenAPI 정보 입력
APP_KEY = 'PSbTf1wtJHwrU3txN6bMQXYOinksGxZzBKP0'
APP_SECRET = 'Qxbk2CWg6WQ4bdI58Mm5NgBggQoXOdxbjHmWnDFPq1OYw+CDhJUqHgvKEWlEyXRC/iYz24ImK6PoLUoRXNhk1s3q50rOHbRGH44C4IeNk07jB6QszK/JK9J89vqCFWWrUwgdl9HItsO4jgx7fBNuEmHqKyV+UcSVQWdh0O6A+TGDFm1kCHk='
URL_BASE = 'https://openapi.koreainvestment.com:9443'

def get_access_token():
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.json())  # 응답 데이터 출력 (디버깅용)
    return response.json()['access_token']

def get_stock_rank(access_token):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-trend-index"
    headers = {
        "authorization": f"Bearer {access_token}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST03010100"
    }
    params = {
        "market_division_code": "J",  # KOSPI: J, KOSDAQ: Q
        "sort_type": "2",             # 등락율순: 2
        "req_cnt": "20"               # 요청 수
    }
    response = requests.get(url, headers=headers, params=params)
    print(response.json())  # 응답 데이터 출력 (디버깅용)
    return response.json()

def main():
    token = get_access_token()
    data = get_stock_rank(token)
    for item in data.get('output', []):
        print(f"{item['hts_kor_isnm']} ({item['shrn_iscd']}): {item['fluc_rt']}%")

if __name__ == "__main__":
    main()