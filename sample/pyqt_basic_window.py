import sys
from PyQt5.QtWidgets import QComboBox, QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class CheckableComboBox(QComboBox):
    # 선택된 항목들이 변경될 때 발생하는 사용자 정의 시그널
    selectionChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        
        # 콤보박스 상단 텍스트를 수정 가능하게 하여 선택 목록 표시 (읽기 전용)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText("항목을 선택하세요")

    def handle_item_pressed(self, index):
        """항목 클릭 시 체크 상태를 반전시킴"""
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        
        self.update_display_text()
        self.selectionChanged.emit(self.current_data())

    def update_display_text(self):
        """선택된 항목들을 콤보박스 텍스트창에 쉼표로 구분하여 표시"""
        selected_texts = self.current_data()
        self.lineEdit().setText(", ".join(selected_texts))

    def addItem(self, text, data=None):
        item = QStandardItem(text)
        item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def current_data(self):
        """체크된 항목들의 텍스트 리스트 반환"""
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).text())
        return res

    def hidePopup(self):
        """항목 클릭 시 팝업이 바로 닫히지 않게 하려면 이 메서드를 제어함"""
        # 기본 동작은 항목 클릭 시 팝업이 닫힘. 
        # 만약 여러 개를 계속 선택하게 하려면 이 부분을 주석 처리하거나 조건부 호출
        super(CheckableComboBox, self).hidePopup()

# --- 실행 예시 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.combo = CheckableComboBox()
        for i in range(5):
            self.combo.addItem(f"옵션 {i+1}")

        # 이벤트 핸들러 연결
        self.combo.selectionChanged.connect(self.on_selection_change)

        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_selection_change(self, selected_list):
        print(f"현재 선택된 항목: {selected_list}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
