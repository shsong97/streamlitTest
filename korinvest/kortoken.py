import requests

app_key = 'PSbTf1wtJHwrU3txN6bMQXYOinksGxZzBKP0'
app_secret = 'Qxbk2CWg6WQ4bdI58Mm5NgBggQoXOdxbjHmWnDFPq1OYw+CDhJUqHgvKEWlEyXRC/iYz24ImK6PoLUoRXNhk1s3q50rOHbRGH44C4IeNk07jB6QszK/JK9J89vqCFWWrUwgdl9HItsO4jgx7fBNuEmHqKyV+UcSVQWdh0O6A+TGDFm1kCHk='

url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
headers = {
    "Content-Type": "application/json; charset=UTF-8"
}
data = {
    "grant_type": "client_credentials",
    "appkey": app_key,
    "appsecret": app_secret
}

print(data)

response = requests.post(url, headers=headers, data=data)
token_json = response.json()
print(token_json)

# access_token 추출
#access_token = token_json['access_token']
#print("Access Token:", access_token)