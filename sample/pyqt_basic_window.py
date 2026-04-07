import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('PyQt5 기본 윈도우')
window.resize(400, 300)
window.show()
sys.exit(app.exec_())
