import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QSplitter
)
import FinanceDataReader as fdr



class StockSearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('주식 종목 검색')
        self.resize(700, 400)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # 좌측: 종목 리스트
        left_layout = QVBoxLayout()
        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText('종목명/코드 필터')
        left_layout.addWidget(self.filter_input)
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(220)
        left_layout.addWidget(self.list_widget)
        main_layout.addLayout(left_layout)

        # 우측: 검색/결과
        right_layout = QVBoxLayout()

        self.input = QLineEdit(self)
        self.input.setPlaceholderText('종목명 또는 코드 입력')
        right_layout.addWidget(self.input)

        self.search_btn = QPushButton('검색', self)
        self.search_btn.clicked.connect(self.search_stock)
        right_layout.addWidget(self.search_btn)

        self.result_label = QLabel('', self)
        self.result_label.setWordWrap(True)
        right_layout.addWidget(self.result_label)

        main_layout.addLayout(right_layout)

        # 종목 데이터 로드
        self.df_kospi = None
        self.df_kosdaq = None
        self.stock_list_data = []  # (market, code, name) 튜플 저장
        self.load_stock_lists()

        # 리스트 클릭 시 상세 표시
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        # 필터 입력 시 리스트 필터링
        self.filter_input.textChanged.connect(self.filter_stock_list)

    def load_stock_lists(self):
        import FinanceDataReader as fdr
        try:
            self.df_kospi = fdr.StockListing('KOSPI')
            self.df_kosdaq = fdr.StockListing('KOSDAQ')
        except Exception as e:
            self.result_label.setText(f'종목 리스트 로드 오류: {e}')
            return
        self.stock_list_data = []
        # KOSPI
        self.stock_list_data.append({'header': 'KOSPI'})
        for _, row in self.df_kospi.iterrows():
            self.stock_list_data.append({'market': 'KOSPI', 'code': row['Code'], 'name': row['Name']})
        # KOSDAQ
        self.stock_list_data.append({'header': 'KOSDAQ'})
        for _, row in self.df_kosdaq.iterrows():
            self.stock_list_data.append({'market': 'KOSDAQ', 'code': row['Code'], 'name': row['Name']})
        self.filter_stock_list()  # 초기 전체 리스트 표시

    def filter_stock_list(self):
        text = self.filter_input.text().strip().lower()
        self.list_widget.clear()
        show_kospi = False
        show_kosdaq = False
        for entry in self.stock_list_data:
            if 'header' in entry:
                if entry['header'] == 'KOSPI':
                    show_kospi = False
                elif entry['header'] == 'KOSDAQ':
                    show_kosdaq = False
                continue  # 헤더는 조건부로 아래에서 추가
            label = f"{entry['name']} ({entry['code']})".lower()
            if text == '' or text in label:
                if entry['market'] == 'KOSPI' and not show_kospi:
                    header_item = QListWidgetItem('--- [KOSPI] ---')
                    header_item.setFlags(header_item.flags() & ~2)  # 비선택
                    self.list_widget.addItem(header_item)
                    show_kospi = True
                if entry['market'] == 'KOSDAQ' and not show_kosdaq:
                    header_item = QListWidgetItem('--- [KOSDAQ] ---')
                    header_item.setFlags(header_item.flags() & ~2)
                    self.list_widget.addItem(header_item)
                    show_kosdaq = True
                item = QListWidgetItem(f"{entry['name']} ({entry['code']})")
                item.setData(32, (entry['market'], entry['code']))
                self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        data = item.data(32)
        if not data or isinstance(data, str):
            return
        market, code = data
        self.show_stock_info(code, market)

    def show_stock_info(self, code, market):
        import yfinance as yf
        try:
            if market == 'KOSPI':
                ticker = f"{code}.KS"
            elif market == 'KOSDAQ':
                ticker = f"{code}.KQ"
            else:
                ticker = code
            # 종목 기본 정보
            if market == 'KOSPI':
                info = self.df_kospi[self.df_kospi['Code'] == code].iloc[0]
            else:
                info = self.df_kosdaq[self.df_kosdaq['Code'] == code].iloc[0]
            stock = yf.Ticker(ticker)
            price = stock.info.get('regularMarketPrice', None)
            volume = stock.info.get('volume', None)
            change = stock.info.get('regularMarketChangePercent', None)
            price_str = f"현재가: {price}원" if price is not None else "현재가 정보를 가져올 수 없음"
            volume_str = f"거래량: {volume:,}" if volume is not None else "거래량 정보를 가져올 수 없음"
            if change is not None:
                change_str = f"등락률: {change:.2f}%"
            else:
                change_str = "등락률 정보를 가져올 수 없음"
            self.result_label.setText(f"{info['Name']} ({info['Code']})\n시장: {info['Market']}\n{price_str}\n{volume_str}\n{change_str}")
        except Exception as e:
            self.result_label.setText(f'오류: {e}')

    def search_stock(self):
        keyword = self.input.text().strip()
        if not keyword:
            self.result_label.setText('검색어를 입력하세요.')
            return
        try:
            import yfinance as yf
            import FinanceDataReader as fdr
            df = fdr.StockListing('KRX')
            result = df[(df['Name'].str.contains(keyword, case=False, na=False)) | (df['Code'].str.contains(keyword))]
            if result.empty:
                self.result_label.setText('검색 결과가 없습니다.')
            else:
                info = result.iloc[0]
                code = info['Code']
                market = info['Market']
                if market == 'KOSPI':
                    ticker = f"{code}.KS"
                elif market == 'KOSDAQ':
                    ticker = f"{code}.KQ"
                else:
                    ticker = code
                stock = yf.Ticker(ticker)
                price = stock.info.get('regularMarketPrice', None)
                volume = stock.info.get('volume', None)
                change = stock.info.get('regularMarketChangePercent', None)
                price_str = f"현재가: {price}원" if price is not None else "현재가 정보를 가져올 수 없음"
                volume_str = f"거래량: {volume:,}" if volume is not None else "거래량 정보를 가져올 수 없음"
                if change is not None:
                    change_str = f"등락률: {change:.2f}%"
                else:
                    change_str = "등락률 정보를 가져올 수 없음"
                self.result_label.setText(f"{info['Name']} ({info['Code']})\n시장: {info['Market']}\n{price_str}\n{volume_str}\n{change_str}")
        except Exception as e:
            self.result_label.setText(f'오류: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockSearchWindow()
    window.show()
    sys.exit(app.exec_())
