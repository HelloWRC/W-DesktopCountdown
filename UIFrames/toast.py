from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, Qt
from UIFrames.ui_toast import Ui_Toast

showed_toasts = None


class Toast(QDialog):
    def __init__(self, parent, text, timeout):
        super(Toast, self).__init__()
        self.parent_w = parent
        self.ui = Ui_Toast()
        self.ui.setupUi(self)
        self.ui.label.setText(text)
        self.timer = QTimer()
        self.timer.setInterval(timeout)
        self.timer.timeout.connect(self.close)
        self.timer.start()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        effect = QGraphicsDropShadowEffect(self)
        effect.setOffset(0, 0)
        effect.setColor(Qt.black)
        effect.setBlurRadius(20)
        self.ui.frame.setGraphicsEffect(effect)

    def showEvent(self, a0) -> None:
        # set window pos
        self.set_pos()
    
    def show(self) -> None:
        super(Toast, self).show()
        self.setParent(self.parent_w)
        super(Toast, self).show()
    
    def paintEvent(self, a0) -> None:
        self.set_pos()

    def closeEvent(self, a0) -> None:
        self.timer.stop()

    def set_pos(self):
        px = self.parent_w.pos().x()
        py = self.parent_w.pos().y()
        pw = self.parent_w.size().width()
        ph = self.parent_w.size().height()
        w = self.size().width()

        x = int(pw / 2 - w / 2)
        y = int(ph - 150)

        self.move(x, y)

    # slots
    def on_btn_close_released(self):
        self.close()

    @staticmethod
    def show_toast(parent, text, timeout):
        global showed_toasts
        toast = showed_toasts = Toast(parent, text, timeout)
        toast.show()
