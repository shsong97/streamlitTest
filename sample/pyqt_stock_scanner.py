import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, 
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import FinanceDataReader as fdr
import traceback
import time
import os

import requests

# korbacktest.py의 scan_stock_list 함수 임포트
from korbacktest import _prepare_indicator_df, buy_combos

# Telegram Bot Token과 Chat ID를 .env 파일에서 읽기
import os
from dotenv import load_dotenv
load_dotenv()
token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

class ScanThread(QThread):
    result_signal = pyqtSignal(pd.DataFrame)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int, str, str)  # current, total, code, name

    def __init__(self, market, recent_days, kospi_count, buy_signal_names, parent=None):
        super().__init__(parent)
        self.market = market
        self.recent_days = recent_days
        self.kospi_count = kospi_count
        self.buy_signal_names = buy_signal_names

    def run(self):
        try:
            if '전체' in self.buy_signal_names:
                combos = buy_combos
            else:
                combos = [combo for combo in buy_combos if combo["name"] in self.buy_signal_names]
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
    def on_table_cell_clicked(self, row, column):
        # 0번 컬럼(티커) 클릭 시 네이버 금융 링크 열기
        if column == 0:
            item = self.table.item(row, column)
            if item:
                url = item.data(Qt.UserRole)
                if url:
                    import webbrowser
                    webbrowser.open(url)
    def show_result(self, df):
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f'검색 완료: {len(df)}개 종목')
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.current_code_label.setText('')
        self.table.setRowCount(0)
        self._last_result_df = df
        # 검색이 완료된 후에만 텔레그램 버튼 활성화
        if df is None or df.empty:
            self.telegram_btn.setEnabled(False)
            return
        else:
            self.telegram_btn.setEnabled(True)
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            ticker = str(row.get('ticker', ''))
            name = str(row.get('name', ''))
            buy_signal = str(row.get('buy_signal', ''))
            buy_date = str(row.get('buy_date', ''))
            # 네이버 금융 차트 링크 생성 (티커에서 코드만 추출)
            code = ticker.split('.')[0] if '.' in ticker else ticker
            naver_url = f"https://finance.naver.com/item/fchart.naver?code={code}"
            code_item = QTableWidgetItem(f"<a href='{naver_url}'>{code}</a>")
            code_item.setFlags(code_item.flags() & ~Qt.ItemIsEditable)
            code_item.setData(Qt.UserRole, naver_url)
            self.table.setItem(i, 0, code_item)
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(buy_signal))
            self.table.setItem(i, 3, QTableWidgetItem(buy_date))

        # 테이블에서 HTML 링크가 보이도록 delegate 설정
        from PyQt5.QtWidgets import QStyledItemDelegate
        class HTMLDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                from PyQt5.QtGui import QTextDocument
                doc = QTextDocument()
                doc.setHtml(index.data())
                painter.save()
                painter.translate(option.rect.topLeft())
                doc.drawContents(painter)
                painter.restore()
            def sizeHint(self, option, index):
                from PyQt5.QtGui import QTextDocument
                doc = QTextDocument()
                doc.setHtml(index.data())
                return doc.size().toSize()
        self.table.setItemDelegateForColumn(0, HTMLDelegate(self.table))

    def send_telegram(self):
        # 테이블에서 종목코드, 종목명, 매수신호 추출
        row_count = self.table.rowCount()
        if row_count == 0:
            self.status_label.setText('전송할 검색 결과가 없습니다.')
            return
        items = []
        for i in range(row_count):
            code = self.table.item(i, 0).text() if self.table.item(i, 0) else ''
            name = self.table.item(i, 1).text() if self.table.item(i, 1) else ''
            buy_signal = self.table.item(i, 2).text() if self.table.item(i, 2) else ''
            if code and name:
                # 매수신호가 있으면 같이 표시
                if buy_signal:
                    items.append(f"{code} : {name} [{buy_signal}]")
                else:
                    items.append(f"{code} : {name}")
        if not items:
            self.status_label.setText('전송할 검색 결과가 없습니다.')
            return
        import datetime
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        title = f"검색 매수 종목 ({today})"
        msg = f"{title}\n\n" + '\n'.join(items)
        resp = self.send_telegram_message(msg)
        if resp.get('ok'):
            self.status_label.setText('텔레그램 전송 완료!')
        else:
            self.status_label.setText(f"텔레그램 전송 실패: {resp}")


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
        view = self.buy_combo_combo.view()
        view.clicked.connect(self.handle_check)
        model = QStandardItemModel()
        all_item = QStandardItem('전체')
        all_item.setCheckable(True)
        model.appendRow(all_item)
        for combo in buy_combos:
            item = QStandardItem(combo['name'])
            item.setCheckable(True)
            model.appendRow(item)
        self.buy_combo_combo.setModel(model)
        option_layout.addWidget(QLabel('매수신호:'))
        option_layout.addWidget(self.buy_combo_combo)


        self.count_input = QLineEdit(self)
        self.count_input.setPlaceholderText('스캔 종목 수')
        self.count_input.setText('100')
        option_layout.addWidget(QLabel('시총상위:'))
        option_layout.addWidget(self.count_input)
        self.days_input = QLineEdit(self)
        self.days_input.setPlaceholderText('최근 N일')
        self.days_input.setText('10')
        option_layout.addWidget(QLabel('최근 N일:'))
        option_layout.addWidget(self.days_input)
        self.scan_btn = QPushButton('검색 시작', self)
        self.scan_btn.clicked.connect(self.start_scan)
        option_layout.addWidget(self.scan_btn)

        # 텔레그램 전송 버튼
        self.telegram_btn = QPushButton('텔레그램 전송', self)
        self.telegram_btn.clicked.connect(self.send_telegram)
        self.telegram_btn.setEnabled(False)
        option_layout.addWidget(self.telegram_btn)

        # self.single_code_input = QLineEdit(self)
        # self.single_code_input.setPlaceholderText('종목코드 (예: 005930)')
        # option_layout.addWidget(self.single_code_input)
        # self.single_scan_btn = QPushButton('단일검색', self)
        # self.single_scan_btn.clicked.connect(self.single_scan)
        # option_layout.addWidget(self.single_scan_btn)
        
        main_layout.addLayout(option_layout)

        # 2번째 줄: 단일검색 위젯
        single_layout = QHBoxLayout()
        self.single_code_input = QLineEdit(self)
        self.single_code_input.setPlaceholderText('종목코드 (예: 005930)')
        single_layout.addWidget(QLabel('단일검색:'))
        single_layout.addWidget(self.single_code_input)
        self.single_scan_btn = QPushButton('단일검색', self)
        self.single_scan_btn.clicked.connect(self.single_scan)
        single_layout.addWidget(self.single_scan_btn)
        main_layout.addLayout(single_layout)

        
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
        self.table.setColumnCount(4)  # 종목코드, 종목명, 매수신호, 매수일
        self.table.setHorizontalHeaderLabels(['종목코드', '종목명', '매수신호', '매수일'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # 상태 표시
        self.status_label = QLabel('', self)
        main_layout.addWidget(self.status_label)

        # 테이블 셀 클릭 시 하이퍼링크 열기 연결
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        self.scan_thread = None
    
    # 단일검색 함수 추가
    def single_scan(self):
        code = self.single_code_input.text().strip()
        if not code:
            self.status_label.setText('종목코드를 입력하세요.')
            return
        market = self.market_combo.currentText().strip().upper()
        buy_signal_names = self.get_selected_buy_signals()
        try:
            recent_days = int(self.days_input.text().strip())
        except Exception:
            recent_days = 10
        self.status_label.setText('단일 종목 검색 중...')
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.current_code_label.setText('')
        self.scan_btn.setEnabled(False)
        # market에 맞는 티커 생성
        if market == "KOSPI":
            ticker = f"{code}.KS"
        elif market == "KOSDAQ":
            ticker = f"{code}.KQ"
        else:
            ticker = code
        # 검색 로직 (buy_signal_names에 따라)
        from korbacktest import _prepare_indicator_df, buy_combos
        if '전체' in buy_signal_names:
            combos = buy_combos
        else:
            combos = [combo for combo in buy_combos if combo["name"] in buy_signal_names]
        try:
            df = _prepare_indicator_df(ticker)
            if df is None:
                self.status_label.setText('데이터를 불러올 수 없습니다.')
                return
            buy_dates = []
            buy_combo_names = []
            for combo in combos:
                signal = combo['signal'](df)
                recent_hits = signal.tail(recent_days)
                hits = list(recent_hits[recent_hits].index)
                if hits:
                    buy_dates.extend(hits)
                    buy_combo_names.append(combo['name'])
            if buy_dates:
                last_buy = max(buy_dates).date().isoformat()
                result = [{
                    "ticker": ticker,
                    "name": code,
                    "buy_signal": ", ".join(buy_combo_names) if buy_combo_names else "-",
                    "buy_date": last_buy,
                }]
                import pandas as pd
                self.show_result(pd.DataFrame(result))
            else:
                self.status_label.setText('매수신호 조건에 해당 없음')
        except Exception as e:
            self.status_label.setText(f'오류: {e}')
        self.scan_btn.setEnabled(True)

    def handle_check(self, index):
        item = self.buy_combo_combo.model().itemFromIndex(index)
        if item is not None:
            if item.text() == '전체':
                # 전체가 체크되면 나머지 모두 체크
                for i in range(1, self.buy_combo_combo.model().rowCount()):
                    other_item = self.buy_combo_combo.model().item(i)
                    if other_item is not None:
                        other_item.setCheckState(item.checkState())
            else:
                # 개별이 체크되면 전체는 해제
                all_item = self.buy_combo_combo.model().item(0)
                if all_item is not None and item.checkState() == Qt.Unchecked:
                    all_item.setCheckState(Qt.Unchecked)

    def get_selected_buy_signals(self):
        selected_names = []
        for i in range(self.buy_combo_combo.model().rowCount()):
            item = self.buy_combo_combo.model().item(i)
            if item.checkState() == Qt.Checked:
                selected_names.append(item.text())
        return selected_names
    
    def start_scan(self):
        market = self.market_combo.currentText().strip().upper()
        buy_signal_names = self.get_selected_buy_signals()
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
        self.scan_thread = ScanThread(market, recent_days, kospi_count, buy_signal_names)
        self.scan_thread.result_signal.connect(self.show_result)
        self.scan_thread.error_signal.connect(self.show_error)
        self.scan_thread.progress_signal.connect(self.update_progress)

        self.scan_thread.start()


    def update_progress(self, current, total, code, name):
        # 프로그레스바를 0~total로 설정하고 현재값을 current로
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.current_code_label.setText(f'현재: {code} ({name})')

    # Telegram 메시지 전송 함수 (#sym:send_telegram_message)
    def send_telegram_message(self, message):
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        response = requests.post(url, data=data)
        return response.json()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockScannerWindow()
    window.show()
    sys.exit(app.exec_())

