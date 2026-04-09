import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import FinanceDataReader as fdr
import traceback
import time
import os

# korbacktest.py의 scan_stock_list 함수 임포트
from korbacktest import _prepare_indicator_df, scan_stock_list, buy_combos

class ScanThread(QThread):
    result_signal = pyqtSignal(pd.DataFrame)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int, str, str)  # current, total, code, name

    def __init__(self, market, recent_days, kospi_count, buy_signal_name, parent=None):
        super().__init__(parent)
        self.market = market
        self.recent_days = recent_days
        self.kospi_count = kospi_count
        self.buy_signal_name = buy_signal_name

    def run(self):
        try:
            # 콤보박스에서 선택한 신호명 또는 '전체'에 따라 검색
            if self.buy_signal_name == '전체':
                combos = buy_combos
            else:
                combos = [combo for combo in buy_combos if combo["name"] == self.buy_signal_name]
            df_krx = fdr.StockListing(self.market)
            mcap_col = next((col for col in ['MarCap', 'Marcap', 'MarketCap'] if col in df_krx.columns), None)
            if not mcap_col:
                raise ValueError(f"Market cap column not found. Available columns: {list(df_krx.columns)}")
            top_list = df_krx.sort_values(by=mcap_col, ascending=False).head(self.kospi_count)

            results = []
            num_count = 0
            total = len(top_list)
            for _, row in top_list.iterrows():
                symbol, name = row['Code'], row['Name']
                if self.market == "KOSPI":
                    ticker = f"{symbol}.KS"
                elif self.market == "KOSDAQ":
                    ticker = f"{symbol}.KQ"
                else:
                    ticker = symbol
                num_count += 1
                self.progress_signal.emit(num_count, total, ticker, name)
                df = None
                try:
                    df = _prepare_indicator_df(ticker)
                except Exception:
                    pass
                if df is None:
                    continue
                buy_dates = []
                buy_combo_names = []
                for combo in combos:
                    signal = combo['signal'](df)
                    recent_hits = signal.tail(self.recent_days)
                    hits = list(recent_hits[recent_hits].index)
                    if hits:
                        buy_dates.extend(hits)
                        buy_combo_names.append(combo['name'])
                if buy_dates:
                    last_buy = max(buy_dates).date().isoformat() if buy_dates else "-"
                    results.append({
                        "ticker": ticker,
                        "name": name,
                        "buy_signal": ", ".join(buy_combo_names) if buy_combo_names else "-",
                        "buy_date": last_buy,
                        "sell_signal": "-",
                        "sell_date": "-",
                    })
            df_result = pd.DataFrame(results)
            self.result_signal.emit(df_result)
        except Exception as e:
            tb = traceback.format_exc()
            self.error_signal.emit(f"오류: {e}\n{tb}")


class StockScannerWindow(QWidget):

    def show_result(self, df):
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f'검색 완료: {len(df)}개 종목')
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.current_code_label.setText('')
        self.table.setRowCount(0)
        if df is None or df.empty:
            return
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get('ticker', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get('name', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(row.get('buy_signal', ''))))
            self.table.setItem(i, 3, QTableWidgetItem(str(row.get('buy_date', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(str(row.get('sell_signal', ''))))
            self.table.setItem(i, 5, QTableWidgetItem(str(row.get('sell_date', ''))))

    def show_error(self, msg):
        self.scan_btn.setEnabled(True)
        self.status_label.setText(msg)
        self.progress_bar.setValue(0)
        self.current_code_label.setText('')
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle('추천 검색 조건 주식 스캐너')
        self.resize(900, 650)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 상단: 검색 옵션
        from PyQt5.QtWidgets import QComboBox
        option_layout = QHBoxLayout()
        self.market_combo = QComboBox(self)
        self.market_combo.addItems(['KOSPI', 'KOSDAQ'])
        option_layout.addWidget(QLabel('시장:'))
        option_layout.addWidget(self.market_combo)

        # 매수신호 콤보박스
        self.buy_combo_combo = QComboBox(self)
        self.buy_combo_combo.addItem('전체')
        self.buy_combo_combo.addItems([combo['name'] for combo in buy_combos])
        option_layout.addWidget(QLabel('매수신호:'))
        option_layout.addWidget(self.buy_combo_combo)
        self.count_input = QLineEdit(self)
        self.count_input.setPlaceholderText('스캔 종목 수')
        self.count_input.setText('100')
        option_layout.addWidget(QLabel('종목 수:'))
        option_layout.addWidget(self.count_input)
        self.days_input = QLineEdit(self)
        self.days_input.setPlaceholderText('최근 N일')
        self.days_input.setText('10')
        option_layout.addWidget(QLabel('최근 N일:'))
        option_layout.addWidget(self.days_input)
        self.scan_btn = QPushButton('검색 시작', self)
        self.scan_btn.clicked.connect(self.start_scan)
        option_layout.addWidget(self.scan_btn)
        main_layout.addLayout(option_layout)

        # 진행률 바 (QGroupBox로 감싸서 구분)
        from PyQt5.QtWidgets import QGroupBox
        progress_group = QGroupBox('진행 상태')
        progress_group_layout = QVBoxLayout()
        progress_group.setLayout(progress_group_layout)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)  # 임시, 검색 시작 시 동적으로 변경
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                margin: 6px;
                font-weight: bold;
                border: 1px solid #bbb;
                border-radius: 8px;
                background: #f5f5f5;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 8px;
            }
        ''')
        progress_layout.addWidget(QLabel('진행률:'))
        progress_layout.addWidget(self.progress_bar, stretch=2)
        self.current_code_label = QLabel('')
        self.current_code_label.setStyleSheet('margin-left: 12px; font-size: 13px; color: #333;')
        progress_layout.addWidget(self.current_code_label, stretch=1)
        progress_group_layout.addLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # 결과 테이블
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['티커', '종목명', '매수신호', '매수일', '매도신호', '매도일'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # 상태 표시
        self.status_label = QLabel('', self)
        main_layout.addWidget(self.status_label)

        self.scan_thread = None

    def start_scan(self):
        market = self.market_combo.currentText().strip().upper()
        buy_signal_name = self.buy_combo_combo.currentText().strip()
        try:
            kospi_count = int(self.count_input.text().strip())
        except Exception:
            kospi_count = 100
        try:
            recent_days = int(self.days_input.text().strip())
        except Exception:
            recent_days = 10
        self.status_label.setText('검색 중...')
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(int(self.count_input.text().strip()) if self.count_input.text().strip().isdigit() else 100)
        self.current_code_label.setText('')
        self.scan_btn.setEnabled(False)
        self.scan_thread = ScanThread(market, recent_days, kospi_count, buy_signal_name)
        self.scan_thread.result_signal.connect(self.show_result)
        self.scan_thread.error_signal.connect(self.show_error)
        self.scan_thread.progress_signal.connect(self.update_progress)

        self.scan_thread.start()


    def update_progress(self, current, total, code, name):
        # 프로그레스바를 0~total로 설정하고 현재값을 current로
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.current_code_label.setText(f'현재: {code} ({name})')

    class ScanThread(QThread):
        result_signal = pyqtSignal(pd.DataFrame)
        error_signal = pyqtSignal(str)
        progress_signal = pyqtSignal(int, int, str, str)  # current, total, code, name

        def __init__(self, market, recent_days, kospi_count, buy_signal_name, parent=None):
            super().__init__(parent)
            self.market = market
            self.recent_days = recent_days
            self.kospi_count = kospi_count
            self.buy_signal_name = buy_signal_name

        def run(self):
            try:
                if self.buy_signal_name == '전체':
                    combos = buy_combos
                else:
                    combos = [combo for combo in buy_combos if combo["name"] == self.buy_signal_name]
                df_krx = fdr.StockListing(self.market)
                mcap_col = next((col for col in ['MarCap', 'Marcap', 'MarketCap'] if col in df_krx.columns), None)
                if not mcap_col:
                    raise ValueError(f"Market cap column not found. Available columns: {list(df_krx.columns)}")
                top_list = df_krx.sort_values(by=mcap_col, ascending=False).head(self.kospi_count)

                results = []
                num_count = 0
                total = len(top_list)
                for _, row in top_list.iterrows():
                    symbol, name = row['Code'], row['Name']
                    if self.market == "KOSPI":
                        ticker = f"{symbol}.KS"
                    elif self.market == "KOSDAQ":
                        ticker = f"{symbol}.KQ"
                    else:
                        ticker = symbol
                    num_count += 1
                    self.progress_signal.emit(num_count, total, ticker, name)
                    df = None
                    try:
                        df = _prepare_indicator_df(ticker)
                    except Exception:
                        pass
                    if df is None:
                        continue
                    buy_dates = []
                    buy_combo_names = []
                    for combo in combos:
                        signal = combo['signal'](df)
                        recent_hits = signal.tail(self.recent_days)
                        hits = list(recent_hits[recent_hits].index)
                        if hits:
                            buy_dates.extend(hits)
                            buy_combo_names.append(combo['name'])
                    if buy_dates:
                        last_buy = max(buy_dates).date().isoformat() if buy_dates else "-"
                        results.append({
                            "ticker": ticker,
                            "name": name,
                            "buy_signal": ", ".join(buy_combo_names) if buy_combo_names else "-",
                            "buy_date": last_buy,
                            "sell_signal": "-",
                            "sell_date": "-",
                        })
                df_result = pd.DataFrame(results)
                self.result_signal.emit(df_result)
            except Exception as e:
                tb = traceback.format_exc()
                self.error_signal.emit(f"오류: {e}\n{tb}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockScannerWindow()
    window.show()
    sys.exit(app.exec_())

