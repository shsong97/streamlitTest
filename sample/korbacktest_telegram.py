import korbacktest as korbacktest
import requests
import datetime
import schedule
import time

# Telegram Bot Token과 Chat ID를 .env 파일에서 읽기
import os
from dotenv import load_dotenv
load_dotenv()
token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# buy_combos와 sell_combos 정의 (korbacktest.py에서 복사)
buy_combos = [
    {
        "name": "매수타임",
        "signal": lambda d: (d['MACD'] > d['MACD_Signal']) 
                            & (d['MACD'].shift(1) <= d['MACD_Signal'].shift(1))
                            & (d['MACD'] < 0)
                            & (d['Close'] > d['MA_5'])
                            & (d['Volume'] > d['Vol_Avg']),
    },
]

# Telegram 메시지 전송 함수
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, data=data)
    return response.json()

# 매수 종목 스캔 및 메시지 전송 함수
def send_daily_stock_message():
    result_df = korbacktest.scan_stock_list(
        korstr="KOSPI",  # "KOSPI" 또는 "KOSDAQ"
        buy_combos=buy_combos,
        sell_combos=None,
        kospi_count=100,
        recent_days=3,
    )
    if not result_df.empty:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        title = f"오늘 매수 종목 ({today})"
        msg_body = '\n'.join([
            f"{row['ticker']} : {row['name']}" for _, row in result_df[['ticker', 'name']].iterrows()
        ])
        msg = f"{title}\n\n{msg_body}"
        send_telegram_message(msg)
    else:
        send_telegram_message('조건에 맞는 종목이 없습니다.')


#send_daily_stock_message()  # 프로그램 시작 시 즉시 실행

# 매일 10시에 실행
# schedule.every().day.at("10:00").do(send_daily_stock_message)

# print("[INFO] 스케줄러가 시작되었습니다. 매일 10시에 메시지를 전송합니다.")
# while True:
#     schedule.run_pending()
#     time.sleep(30)
