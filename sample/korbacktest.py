import yfinance as yf
import pandas as pd
import pandas_ta as ta
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import mplcursors
import sys
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
from matplotlib import font_manager as fm
font_candidates = [
    "NanumGothic", "Nanum Gothic", "Apple SD Gothic Neo", "AppleGothic", "BM Jua", "BM Hanna", "BM Kirang Haerang", "Malgun Gothic", "Noto Sans KR", "Noto Sans CJK KR"
]
found_font = None
for font_name in font_candidates:
    matches = [f for f in fm.fontManager.ttflist if font_name in f.name]
    if matches:
        found_font = matches[0]
        break
if found_font:
    font_prop = fm.FontProperties(fname=found_font.fname)
    matplotlib.rcParams['font.family'] = font_prop.get_name()
    matplotlib.rcParams['font.sans-serif'] = [font_prop.get_name()]
else:
    font_prop = None

def _prepare_indicator_df(ticker_symbol):
    """종목 데이터를 내려받아 백테스트용 보조지표(RSI, BB, MA, MFI, StochRSI)를 계산해 반환한다."""
    df = yf.download(ticker_symbol, period="1y", interval="1d", progress=False)
    if len(df) < 30:
        print(f"{ticker_symbol}: 데이터가 부족합니다.")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.droplevel(1)

    na_counts = df[['Open', 'High', 'Low', 'Close', 'Volume']].isna().sum()
    if na_counts.any():
        print(f"{ticker_symbol}: 결측치 감지\n{na_counts}")
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
        if len(df) < 30:
            print(f"{ticker_symbol}: 결측 제거 후 데이터가 부족합니다.")
            return None

    close_na_before = df['Close'].isna().sum()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    close_na_after = df['Close'].isna().sum()
    if close_na_after > close_na_before:
        print(f"{ticker_symbol}: Close 비정상 값 발견({close_na_after - close_na_before}건)")
        df = df.dropna(subset=['Close'])
        if len(df) < 30:
            print(f"{ticker_symbol}: Close 정리 후 데이터가 부족합니다.")
            return None

    df['RSI'] = ta.rsi(df['Close'], length=14)
    bbands = ta.bbands(df['Close'], length=20, std=2)
    if bbands is None or bbands.empty:
        print(f"{ticker_symbol}: 볼린저 밴드 계산 실패(데이터 부족 또는 결측).")
        print(f"{ticker_symbol}: 컬럼 목록 {list(df.columns)}")
        print(f"{ticker_symbol}: 샘플 데이터(head)\n{df[['Open','High','Low','Close','Volume']].head(3)}")
        print(f"{ticker_symbol}: 샘플 데이터(tail)\n{df[['Open','High','Low','Close','Volume']].tail(3)}")
        return None

    def _pick_bband_col(prefix: str) -> str:
        """볼린저밴드 결과 컬럼 중 접두사(BBL/BBM/BBU)에 맞는 첫 컬럼명을 찾는다."""
        matches = [c for c in bbands.columns if c.startswith(prefix)]
        return matches[0] if matches else ""

    lower_col = _pick_bband_col("BBL_")
    middle_col = _pick_bband_col("BBM_")
    upper_col = _pick_bband_col("BBU_")
    if not (lower_col and middle_col and upper_col):
        print(f"{ticker_symbol}: 볼린저 밴드 컬럼 확인 필요 {list(bbands.columns)}")
        return None

    df['BB_Lower'] = bbands[lower_col]
    df['BB_Middle'] = bbands[middle_col]
    df['BB_Upper'] = bbands[upper_col]
    df['Vol_Avg'] = df['Volume'].rolling(window=5).mean()

    df = df.sort_index()
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()

    mfi_series = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
    if mfi_series is None or mfi_series.empty:
        df['MFI'] = pd.Series(index=df.index, dtype="float64")
    else:
        df['MFI'] = mfi_series

    stoch_rsi = ta.stochrsi(df['Close'], length=14, rsi_length=14, k=3, d=3)
    if stoch_rsi is None or stoch_rsi.empty:
        df['K'] = pd.Series(index=df.index, dtype="float64")
        df['D'] = pd.Series(index=df.index, dtype="float64")
    else:
        df['K'] = stoch_rsi['STOCHRSIk_14_14_3_3']
        df['D'] = stoch_rsi['STOCHRSId_14_14_3_3']

    # MACD 및 Signal 계산
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_Signal'] = macd['MACDs_12_26_9']
    else:
        df['MACD'] = pd.Series(index=df.index, dtype="float64")
        df['MACD_Signal'] = pd.Series(index=df.index, dtype="float64")
    return df

def run_backtest_and_visualize(ticker_symbol, buy_combos, sell_combos=None, hold_days=10):
    """매수/매도 조합별 신호 성과를 계산하고, 발생한 전체 신호를 한 차트에 시각화한다."""
    df = _prepare_indicator_df(ticker_symbol)
    if df is None:
        return None


    # 4. 수익률 계산 (매수 후 hold_days 거래일 뒤 매도 가정)
    df['Return'] = df['Close'].shift(-hold_days) / df['Close'] - 1


    def _plot_signals(plot_df, buy_signals_df, sell_signals_df=None):
        """가격/볼린저밴드/RSI/MACD와 함께 매수(▲), 매도(▼) 신호를 표시하고, 신호 이름도 함께 표시한다."""
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 14), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})

        # 가격 및 볼린저밴드
        ax1.plot(plot_df.index, plot_df['Close'], label='Close Price', color='blue', linewidth=1)
        ax1.plot(plot_df.index, plot_df['BB_Upper'], label='BB Upper', color='grey', linestyle='--', linewidth=0.8)
        ax1.plot(plot_df.index, plot_df['BB_Middle'], label='BB Middle', color='orange', linestyle='--', linewidth=0.8)
        ax1.plot(plot_df.index, plot_df['BB_Lower'], label='BB Lower', color='grey', linestyle='--', linewidth=0.8)


        # 매수 신호 마커 및 hover 툴팁
        buy_scatter = None
        buy_annotations = []
        if not buy_signals_df.empty:
            buy_scatter = ax1.scatter(buy_signals_df.index, buy_signals_df['Low'], marker='^', s=200, color='green', alpha=0.7, label='Buy Signal', zorder=5)
            buy_annotations = buy_signals_df['Signal_Name'].tolist() if 'Signal_Name' in buy_signals_df.columns else ['']*len(buy_signals_df)

        # 매도 신호 마커 및 hover 툴팁
        sell_scatter = None
        sell_annotations = []
        if sell_signals_df is not None and not sell_signals_df.empty:
            sell_scatter = ax1.scatter(sell_signals_df.index, sell_signals_df['High'], marker='v', s=200, color='red', alpha=0.7, label='Sell Signal', zorder=6)
            sell_annotations = sell_signals_df['Signal_Name'].tolist() if 'Signal_Name' in sell_signals_df.columns else ['']*len(sell_signals_df)

        # mplcursors로 hover 시 신호명 표시
        if buy_scatter is not None and font_prop is not None:
            cursor_buy = mplcursors.cursor(buy_scatter, hover=True)
            @cursor_buy.connect("add")
            def on_add_buy(sel):
                idx = sel.index
                if idx is not None and idx < len(buy_annotations):
                    sel.annotation.set_text(buy_annotations[idx])
                    try:
                        sel.annotation.set_fontproperties(font_prop)
                    except Exception:
                        pass
        if sell_scatter is not None and font_prop is not None:
            cursor_sell = mplcursors.cursor(sell_scatter, hover=True)
            @cursor_sell.connect("add")
            def on_add_sell(sel):
                idx = sel.index
                if idx is not None and idx < len(sell_annotations):
                    sel.annotation.set_text(sell_annotations[idx])
                    try:
                        sel.annotation.set_fontproperties(font_prop)
                    except Exception:
                        pass

        # ticker_symbol이 "005930.KS"와 같이 코드만 있을 때 이름을 붙여서 표시
        stock_name = None
        if hasattr(plot_df, 'attrs') and 'stock_name' in plot_df.attrs:
            stock_name = plot_df.attrs['stock_name']
        elif 'Name' in plot_df.columns:
            stock_name = plot_df['Name'].iloc[0]
        # run_backtest_and_visualize에서 이름을 전달받지 못하면 ticker_symbol만 표시
        title_str = f'{ticker_symbol}'
        if stock_name:
            title_str += f' ({stock_name})'
        title_str += ' Price Chart'
        ax1.set_title(title_str, fontsize=16)
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend()
        ax1.grid(True)

        # RSI
        ax2.plot(plot_df.index, plot_df['RSI'], label='RSI (14)', color='purple', linewidth=1)
        ax2.axhline(30, linestyle='--', color='red', alpha=0.7, label='RSI 30 (Oversold)')
        ax2.axhline(70, linestyle='--', color='blue', alpha=0.7, label='RSI 70 (Overbought)')
        ax2.axhline(35, linestyle=':', color='gray', alpha=0.7, label='RSI 35 (Condition)')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.legend()
        ax2.grid(True)

        # MACD & Signal
        ax3.plot(plot_df.index, plot_df['MACD'], label='MACD', color='black', linewidth=1)
        ax3.plot(plot_df.index, plot_df['MACD_Signal'], label='MACD Signal', color='red', linewidth=1)
        ax3.axhline(0, linestyle='--', color='gray', alpha=0.7)
        ax3.set_ylabel('MACD', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.legend()
        ax3.grid(True)

        plt.tight_layout()
        plt.show()

    # 5. 여러 조합 결과 요약
    results = {}
    buy_signal_frames = []
    buy_hit_combo_names = []
    signal_counts = []
    for combo in buy_combos:
        name = combo['name']
        signal = combo['signal'](df)
        df['Signal'] = signal
        signals = df[df['Signal'] == True].copy()
        signals['Signal_Name'] = name  # 신호명 컬럼 추가
        results[name] = signals[['Close', 'RSI', 'Return', 'Signal_Name']]
        signal_counts.append((name, len(signals)))

        if not signals.empty:
            win_rate = (signals['Return'] > 0).mean() * 100
            avg_ret = signals['Return'].mean() * 100
            print(f"\n[{ticker_symbol}] 조합: {name}")
            print(f"  총 신호 발생 횟수: {len(signals)}회")
            print(f"  승률 ({hold_days}일 보유): {win_rate:.1f}%")
            print(f"  평균 수익률 ({hold_days}일 보유): {avg_ret:.2f}%")
        else:
            print(f"\n[{ticker_symbol}] 조합: {name} - 신호 없음")

        if signals.empty:
            continue

        buy_signal_frames.append(signals)
        buy_hit_combo_names.append(name)

    # 신호 발생 많은 순으로 정렬
    signal_counts_sorted = sorted(signal_counts, key=lambda x: x[1], reverse=True)
    print("\n[매수 시그널 발생 많은 순 정렬 결과]")
    for name, count in signal_counts_sorted:
        print(f"  {name}: {count}회")

    # 6. 매도 신호 조합 결과 요약
    sell_signal_frames = []
    sell_hit_combo_names = []
    if sell_combos:
        for sell_combo in sell_combos:
            name = sell_combo['name']
            sell_signal = sell_combo['signal'](df)
            df['Sell_Signal'] = sell_signal
            sell_signals = df[df['Sell_Signal'] == True].copy()
            sell_signals['Signal_Name'] = name  # 신호명 컬럼 추가

            if not sell_signals.empty:
                print(f"\n[{ticker_symbol}] 매도 조합: {name}")
                print(f"  총 신호 발생 횟수: {len(sell_signals)}회")
                sell_signal_frames.append(sell_signals)
                sell_hit_combo_names.append(name)
            else:
                print(f"\n[{ticker_symbol}] 매도 조합: {name} - 신호 없음")

    all_buy_signals = pd.concat(buy_signal_frames).sort_index() if buy_signal_frames else pd.DataFrame()
    all_sell_signals = pd.concat(sell_signal_frames).sort_index() if sell_signal_frames else pd.DataFrame()

    if not all_buy_signals.empty:
        all_buy_signals = all_buy_signals[~all_buy_signals.index.duplicated(keep='first')]
    if not all_sell_signals.empty:
        all_sell_signals = all_sell_signals[~all_sell_signals.index.duplicated(keep='first')]

    _plot_signals(df, all_buy_signals, all_sell_signals if not all_sell_signals.empty else None)
    print(
        f"시각화 완료 - 매수 조합({', '.join(buy_hit_combo_names) if buy_hit_combo_names else '없음'}), "
        f"매도 조합({', '.join(sell_hit_combo_names) if sell_hit_combo_names else '없음'})"
    )

    return results

def scan_stock_list(korstr, buy_combos, sell_combos=None, kospi_count=10, recent_days=10):
    """시가총액 상위 종목을 스캔해 최근 기간 내 매수/매도 신호가 나온 종목만 요약 반환한다."""
    df_krx = fdr.StockListing(korstr)
    mcap_col = next((col for col in ['MarCap', 'Marcap', 'MarketCap'] if col in df_krx.columns), None)
    if not mcap_col:
        raise ValueError(f"Market cap column not found. Available columns: {list(df_krx.columns)}")
    top_list = df_krx.sort_values(by=mcap_col, ascending=False).head(kospi_count)

    results = []
    num_count=0
    for _, row in top_list.iterrows():
        symbol, name = row['Code'], row['Name']
        if korstr == "KOSPI":
            ticker = f"{symbol}.KS"
        elif korstr == "KOSDAQ":
            ticker = f"{symbol}.KQ"
        else:
            ticker = symbol

        num_count += 1
        print(f"Scanning {num_count} : {ticker} ({name})")
        df = _prepare_indicator_df(ticker)
        if df is None:
            continue

        buy_dates = []
        buy_combo_names = []
        for combo in buy_combos:
            signal = combo['signal'](df)
            recent_hits = signal.tail(recent_days)
            hits = list(recent_hits[recent_hits].index)
            if hits:
                buy_dates.extend(hits)
                buy_combo_names.append(combo['name'])

        sell_dates = []
        sell_combo_names = []
        if sell_combos:
            for sell_combo in sell_combos:
                sell_signal = sell_combo['signal'](df)
                recent_hits = sell_signal.tail(recent_days)
                hits = list(recent_hits[recent_hits].index)
                if hits:
                    sell_dates.extend(hits)
                    sell_combo_names.append(sell_combo['name'])

        if buy_dates or sell_dates:
            last_buy = max(buy_dates).date().isoformat() if buy_dates else "-"
            last_sell = max(sell_dates).date().isoformat() if sell_dates else "-"
            results.append({
                "ticker": ticker,
                "name": name,
                "buy_signal": ", ".join(buy_combo_names) if buy_combo_names else "-",
                "buy_date": last_buy,
                "sell_signal": ", ".join(sell_combo_names) if sell_combo_names else "-",
                "sell_date": last_sell,
            })

    print(f"{korstr} Stock {kospi_count} scan complete: hits={len(results)}")
    if not results:
        print("최근 조건에 해당하는 종목이 없습니다.")
        return pd.DataFrame(columns=["ticker", "name", "buy_signal", "buy_date", "sell_signal", "sell_date"])

    result_df = pd.DataFrame(results)
    # buy_signal이 많은 순으로 정렬
    def count_buy_signals(row):
        if row['buy_signal'] == '-' or not row['buy_signal']:
            return 0
        return len(row['buy_signal'].split(','))
    result_df['buy_signal_count'] = result_df.apply(count_buy_signals, axis=1)
    result_df = result_df.sort_values(by=['buy_signal_count', 'buy_date', 'sell_date'], ascending=[False, False, False])
    print(f"\n[{korstr} Stock 스캔 결과]")
    print(result_df.drop(columns=['buy_signal_count']).to_string(index=False))
    return result_df.drop(columns=['buy_signal_count'])

# 종목 리스트를 받아 매도 신호만 스캔하는 함수
def scan_sell_signal_list(stock_list, sell_combos=None, recent_days=10):
    """입력된 종목 리스트에서 최근 기간 내 매도 신호가 나온 종목만 요약 반환한다."""
    results = []
    num_count = 0
    for ticker in stock_list:
        num_count += 1
        print(f"Scanning {num_count} : {ticker}")
        df = _prepare_indicator_df(ticker)
        if df is None:
            continue

        sell_dates = []
        sell_combo_names = []
        if sell_combos:
            for sell_combo in sell_combos:
                sell_signal = sell_combo['signal'](df)
                recent_hits = sell_signal.tail(recent_days)
                hits = list(recent_hits[recent_hits].index)
                if hits:
                    sell_dates.extend(hits)
                    sell_combo_names.append(sell_combo['name'])

        if sell_dates:
            last_sell = max(sell_dates).date().isoformat() if sell_dates else "-"
            results.append({
                "ticker": ticker,
                "sell_signal": ", ".join(sell_combo_names) if sell_combo_names else "-",
                "sell_date": last_sell,
            })

    print(f"Stock list scan complete: hits={len(results)}")
    if not results:
        print("최근 조건에 해당하는 종목이 없습니다.")
        return pd.DataFrame(columns=["ticker", "sell_signal", "sell_date"])

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by=["sell_date"], ascending=False)
    print(f"\n[매도 신호 스캔 결과]")
    print(result_df.to_string(index=False))
    return result_df


    

buy_combos = [
    {
        "name": "BB 중단 돌파 매수",
        "signal": lambda d: (d['Close'] > d['BB_Middle'])
                        & (d['Close'].shift(1) <= d['BB_Middle'].shift(1))
                        & (d['Close'] > d['Open'])
                        & (d['Volume'] > d['Vol_Avg']),
    },
    {
        "name": "BB 하단 터치",
        "signal": lambda d: (d['Low'] <= d['BB_Lower']),
    },
    {
        "name": "RSI35 + BB + 거래량",
        "signal": lambda d: (d['RSI'] <= 35)
                            & (d['Low'] <= d['BB_Lower'])
                            & (d['Volume'] > d['Vol_Avg'] * 1.5)
                            & (d['Close'] > d['Open']),
    },
    {
        "name": "StochRSI 골든크로스 + MA 골든크로스",
        "signal": lambda d: (d['K'] > d['D'])
                            & (d['K'].shift(1) <= d['D'].shift(1))
                            & (d['MA_5'] > d['MA_20'])
                            & (d['MA_5'].shift(1) <= d['MA_20'].shift(1)),
    },
    {
        "name": "단타 눌림목",
        "signal": lambda d: (d['RSI'].rolling(5).max().shift(1) >= 70)
                            & (d['RSI'] >= 40) & (d['RSI'] <= 55)
                            & (d['Close'] >= d['MA_20'])
                            & (d['Volume'] <= d['Vol_Avg'])
                            & (d['Close'] > d['Open']),
    },
    {
        "name": "관심바닥",
        "signal": lambda d: (d['RSI'] <=50)
                            & (d['Close'] >= d['MA_5'])
                            & (d['Close'] > d['Open']),
    },
    {
        "name": "MACD 돌파 매수",
        "signal": lambda d: (d['MACD'] > d['MACD_Signal']) 
                            & (d['MACD'].shift(1) <= d['MACD_Signal'].shift(1))
                            & (d['MACD'] < 0),  # MACD가 음수 영역에서 Signal을 돌파할 때만 매수
    },
    
    {
        "name": "추천 검색 조건 조합",
        "signal": lambda d: (
            ((d['BB_Upper'] - d['BB_Lower']) / d['BB_Middle'] < 0.1)  # 변동성 응축
            & (d['MACD'] > d['MACD_Signal'])  # MACD 골든크로스
            & (d['Close'] > d['BB_Middle'])   # 중심선 위
            & (d['Volume'] > d['Volume'].shift(1) * 2)  # 거래량 200% 증가
        ),
    },
    {
        "name": "매수타임", 
        "signal": lambda d: (d['Close'] > d['BB_Middle'])
                        & (d['MACD'] > d['MACD_Signal'])
                        & (d['RSI'] >= 40) & (d['RSI'] <= 60)
                        & (d['Close'] > d['Open'])
                        & (d['Close'].shift(1) > d['Open'].shift(1))  # 오늘과 어제 모두 양봉인 경우로 조건 강화
                        & (d['Volume'] > d['Volume'].shift(1)),  # 오늘 거래량이 어제보다 많은 경우로 조건 강화

    },
]

sell_combos = [
    {
        "name": "RSI70 + BB 상단",
        "signal": lambda d: (d['RSI'] >= 70) & (d['High'] >= d['BB_Upper']),
    },
    {
        "name": "MA 데드크로스",
        "signal": lambda d: (d['MA_5'] < d['MA_20']) & (d['MA_5'].shift(1) >= d['MA_20'].shift(1)),
    },
]

if __name__ == "__main__":

    # 특정 종목에 대해 백테스트 실행 및 시각화
    # run_backtest_and_visualize(
    #     "221800.KQ",  
    #     buy_combos=buy_combos,
    #     sell_combos=sell_combos,
    #     hold_days=5,
    # )

    import time
    start_time = time.time()

    # 매수 종목을 스캔해 최근 신호가 나온 종목 리스트를 출력
    scan_stock_list(
        korstr="KOSPI", # "KOSPI" 또는 "KOSDAQ"
        buy_combos=[combo for combo in buy_combos if combo["name"]=="매수타임"],
        sell_combos=None,
        kospi_count=50,
        recent_days=10,
    )

    # 매입종목 리스트를 넣고 매도신호를 포착
    # scan_sell_signal_list(
    #     stock_list=["005930.KS", "000660.KS", "035420.KS"],  # 예시 종목 리스트
    #     sell_combos=sell_combos,
    #     recent_days=3,
    # )

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n총 실행 시간: {elapsed:.2f}초")

    # macbook 에서 완료 후 비프음 출력(백그라운드로 작업을 하면 사용자가 알수 없어 알림음 추가)
    import os
    # os.system('say "끝났습니다"')

