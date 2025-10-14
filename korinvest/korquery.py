import requests
import json

# --- 1단계: API 키 및 토큰 설정 (사전 준비) ---
# 발급받은 실제 App Key, App Secret, Access Token으로 변경해야 합니다.
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjRiNTYzZjQwLTg4OTAtNDkzYi1iNGFkLTk0YzFlYzg0MDk0YiIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc1OTQ3NDMxNiwiaWF0IjoxNzU5Mzg3OTE2LCJqdGkiOiJQU2JUZjF3dEpId3JVM3R4TjZiTVFYWU9pbmtzR3haekJLUDAifQ.VVxqi8kEcZdChMm4QmmzCPcEfZN0vUVx124Xmembux8r3JAhrnb4rjoWEmW3Q3oaB6ntBwp5cpo4RPl9RhK9xQ"

app_key = 'PSbTf1wtJHwrU3txN6bMQXYOinksGxZzBKP0'
app_secret = 'Qxbk2CWg6WQ4bdI58Mm5NgBggQoXOdxbjHmWnDFPq1OYw+CDhJUqHgvKEWlEyXRC/iYz24ImK6PoLUoRXNhk1s3q50rOHbRGH44C4IeNk07jB6QszK/JK9J89vqCFWWrUwgdl9HItsO4jgx7fBNuEmHqKyV+UcSVQWdh0O6A+TGDFm1kCHk='


# --- 2단계: API 요청 ---
url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-price"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "authorization": f"Bearer {access_token}",
    "appkey": app_key,
    "appsecret": app_secret,
    "custype": "P",
    "tr_id": "FHKST01010400"  # 일별 시세 조회  
}
params = {
    "fid_cond_mrkt_div_code": "J",  # 주식
    "fid_input_iscd": "005930",      # 삼성전자
    "fid_org_adj_prc": "0",          # 수정주가 사용 안함
}

try:
    res = requests.get(url, headers=headers, params=params)
    data = res.json()
    print(json.dumps(data, indent=4, ensure_ascii=False))  # 응답 데이터 출력 (디버깅용)

    # --- 3단계: 응답 데이터 처리 ---
    if data['rt_cd'] == '0':  # 성공적으로 데이터를 받았을 경우
        current_price = data['output']['stck_prpr']  # 현재가
        stock_name = data['output']['hts_kor_isnm']  # 종목명
        print(f"종목명: {stock_name}")
        print(f"현재가: {current_price}원")
    else:
        print(f"API 호출 실패: {data['msg1']}")

except Exception as e:
    print(f"오류 발생: {e}")
