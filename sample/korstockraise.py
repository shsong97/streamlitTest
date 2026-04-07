import FinanceDataReader as fdr
import pandas_ta as ta
import yfinance as yf
import time


def get_semi_list():
    # 1. 코스닥 종목 리스트 불러오기
    df_kosdaq = fdr.StockListing('KOSDAQ')
    
    # 2. 컬럼명 확인 (디버깅용)
    # print(df_kosdaq.columns) 
    
    # 3. 'Sector' 또는 'Industry' 컬럼 찾기
    target_col = None
    for col in ['Sector', 'Industry']:
        if col in df_kosdaq.columns:
            target_col = col
            break
            
    if target_col is None:
        print("섹터/업종 정보를 찾을 수 없습니다. 대신 종목명으로 필터링합니다.")
        # 섹터 컬럼이 없을 경우 종목명에 '반도체'가 들어간 것만이라도 추출
        semi_stocks = df_kosdaq[df_kosdaq['Name'].str.contains('반도체|장비|전자부품', na=False)]
    else:
        # 업종 정보에서 '반도체' 키워드 추출
        semi_stocks = df_kosdaq[df_kosdaq[target_col].str.contains('반도체|장비|전자부품', na=False)]
    
    return semi_stocks


def scan_semiconductor_top_picks():
    print("🔍 반도체 테마 내 프리미엄 급등주 스캔 시작...")
    
    # 1. 코스닥 전체 종목 불러오기
    df_kosdaq = fdr.StockListing('KOSDAQ')
    # print(df_kosdaq.head(5)[5:10])  # 데이터 확인용 출력, 실제로는 제거해도 됨
    # return []  # 실제 스캔 결과를 반환하도록 수정 필요
    # 2. 업종명에 '반도체'가 포함된 종목 필터링
    # (필요에 따라 '전자부품'이나 'IT부품'을 추가할 수 있습니다)
    semi_stocks = get_semi_list() #df_kosdaq[df_kosdaq['Industry'].str.contains('반도체', na=False)]
    
    # 시가총액 순으로 정렬하여 너무 작은 종목은 뒤로 밀기
    semi_stocks = semi_stocks.sort_values(by='Marcap', ascending=False)
    
    premium_hits = []

    for _, row in semi_stocks.iterrows():
        symbol, name = row['Code'], row['Name']
        ticker = f"{symbol}.KQ"
        print(f"⏳ 스캔 중: {name} ({ticker})")
        try:
            # 최근 60일 데이터
            df = yf.download(ticker, period="60d", interval="1d", progress=False)
            if len(df) < 20: continue

            curr = df.iloc[-1]
            prev = df.iloc[-2]
            
            # --- 기술적 지표 계산 ---
            ma5 = df['Close'].rolling(5).mean().iloc[-1]
            ma20 = df['Close'].rolling(20).mean().iloc[-1]
            trading_value = curr['Close'] * curr['Volume'] # 거래대금
            vol_avg_5 = df['Volume'].iloc[-6:-1].mean()    # 5일 평균 거래량
            
            # --- 까다로운 조건 검증 ---
            # 조건 1: 거래대금 50억 이상 (반도체 섹터 특성상 50억으로 조정, 대형주는 100억 권장)
            cond_money = trading_value >= 5_000_000_000 
            
            # 조건 2: 거래량 폭발 (전일 대비가 아니라 5일 평균 대비 300% 이상)
            cond_vol = curr['Volume'] > vol_avg_5 * 3
            
            # 조건 3: 20일선 돌파 및 안착 (골든크로스 혹은 돌파)
            cond_trend = (curr['Close'] > ma20) and (prev['Close'] <= ma20)
            
            # 조건 4: 캔들 몸통이 윗꼬리보다 큼 (강한 마감)
            body_size = abs(curr['Close'] - curr['Open'])
            upper_shadow = curr['High'] - max(curr['Close'], curr['Open'])
            cond_candle = body_size > upper_shadow
            
            # 조건 5: 이격도 (과열 방지, 5일선 기준 107% 이내)
            disparity = (curr['Close'] / ma5) * 100
            cond_disparity = 100 <= disparity <= 107

            if cond_money and cond_vol and cond_trend and cond_candle and cond_disparity:
                premium_hits.append({
                    'name': name,
                    'code': symbol,
                    'price': int(curr['Close']),
                    'change': round((curr['Close']/prev['Close']-1)*100, 2),
                    'value_ok': int(trading_value / 100_000_000)
                })
                print(f"🎯 반도체 포착: {name} (+{premium_hits[-1]['change']}%)")

            time.sleep(0.05)
        except:
            continue
            
    return premium_hits

# 결과 출력
results = scan_semiconductor_top_picks()

# 테스트 실행
# semi_list = get_semi_list()
# print(f"찾은 반도체 관련 종목 수: {len(semi_list)}개")
# print(semi_list[['Code', 'Name']].head())