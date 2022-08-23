from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from UIFrames.ui_toast import Ui_Toast
import time


class Toast(QDialog):
    showed_toast = None

    def __init__(self, parent, text, timeout, buttons, no_default_button):
        super(Toast, self).__init__()
        self.bottom_height_v = 0
        self.parent_w = parent
        self.ui = Ui_Toast()
        self.ui.setupUi(self)
        self.ui.label.setText(text)
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_content)
        self.init_animation = QPropertyAnimation(self, b'bottom_height')
        self.init_animation.setStartValue(-10)
        self.init_animation.setEndValue(150)
        self.init_animation.setDuration(200)
        self.init_animation.setEasingCurve(QEasingCurve.OutQuint)
        self.out_animation = QPropertyAnimation(self, b'bottom_height')
        self.out_animation.setStartValue(150)
        self.out_animation.setEndValue(-10)
        self.out_animation.setDuration(200)
        self.out_animation.setEasingCurve(QEasingCurve.OutQuint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        effect = QGraphicsDropShadowEffect(self)
        effect.setOffset(0, 0)
        effect.setColor(Qt.black)
        effect.setBlurRadius(20)
        self.buttons = buttons
        for i in self.buttons:
            self.ui.custom_buttons.addWidget(i)
        if no_default_button:
            self.ui.btn_close.setVisible(False)
        self.ui.frame.setGraphicsEffect(effect)
        self.show_time = time.time()
        self.close_time = -1
        self.timeout = timeout

    def showEvent(self, a0) -> None:
        # set window pos
        self.set_pos()
        # animation

    def show(self) -> None:
        self.adjustSize()
        self.setParent(self.parent_w)
        super(Toast, self).show()
        self.init_animation.start()
        self.show_time = time.time()
        self.timer.start()

    def pre_close(self):
        if self.close_time != -1:
            return
        self.close_time = time.time()
        self.out_animation.start()

    def paintEvent(self, a0) -> None:
        self.set_pos()

    def update_content(self):
        self.set_pos()

        progress = int((self.show_time + self.timeout - time.time()) / self.timeout * 100)
        self.ui.progress.setValue(progress)
        if time.time() - self.show_time >= self.timeout and self.close_time == -1:
            self.pre_close()
        if time.time() - self.close_time >= 0.2 and self.close_time != -1:
            self.timer.stop()
            self.close()

    def set_pos(self):
        px = self.parent_w.pos().x()
        py = self.parent_w.pos().y()
        pw = self.parent_w.size().width()
        ph = self.parent_w.size().height()
        w = self.size().width()

        x = int(pw / 2 - w / 2)
        y = int(ph - self.bottom_height_v)

        self.move(x, y)

    # slots
    def on_btn_close_released(self):
        self.pre_close()

    def set_bh(self, value):
        self.bottom_height_v = value

    def get_bh(self):
        return self.bottom_height_v

    bottom_height = pyqtProperty(int, fset=set_bh, fget=get_bh)

    @staticmethod
    def toast(parent, text, timeout=5, buttons=None, no_default_button=False):
        """
        显示Toast

        :param parent: 要显示Toast的父窗口
        :param text: Toast内容
        :param timeout: （可选）Toast自动关闭时间（秒），默认值为5
        :param buttons: （可选）Toast上要附加的按钮
        :param no_default_button：（可选）是否显示原有的关闭按钮
        """
        if buttons is None:
            buttons = []
        if Toast.showed_toast is not None:
            Toast.showed_toast.close()
        Toast.showed_toast = Toast(parent, text, timeout, buttons, no_default_button)
        Toast.showed_toast.show()
