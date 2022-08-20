from abc import ABC

from functions.plugins import ConfigureView as CV
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, \
    QColorDialog, QFrame, QFormLayout
from PyQt5.QtGui import QColor
from PyQt5.Qt import QApplication, Qt, QSize


# Static widgets
class Label(CV):
    view_id = 'wdcd.label'
    view_name = '文字'
    can_store = False

    def __init__(self, config, container):
        self.config = config
        self.widget = QLabel()
        label = QLabel(self.config['text'])
        if 'word_warp' in self.config:
            label.setWordWrap(self.config['word_warp'])
        if 'selectable' in self.config:
            if self.config['selectable']:
                label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    def generate_widget(self):
        return self.widget

    def load_val(self, value):
        pass

    def save_val(self):
        pass


class Line(CV):
    view_id = 'wdcd.line'
    view_name = '分割线'
    can_store = False
    auto_construct = False

    def __init__(self, config, container):
        self.config = config
        self.container = container

    def generate_widget(self):
        line = QFrame(self.container)
        line.setMinimumSize(QSize(0, 0))
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.container.layout().setWidget(8, QFormLayout.SpanningRole, line)

    def load_val(self, value):
        pass

    def save_val(self):
        pass


# Valuable widgets
class LCV(CV, ABC):
    def __init__(self, config, container):
        self.content = None
        self.label = QLabel(config['name'])
        if 'description' in config:
            self.label.setToolTip(config['description'])

    def generate_widget(self):
        return self.label, self.content


class CheckBox(CV):
    view_id = 'wdcd.check_box'
    view_name = '复选框'

    def __init__(self, config, container):
        self.config = config
        self.container = container
        self.checkbox = QCheckBox(config['name'])
        if 'description' in config:
            self.checkbox.setToolTip(config['description'])

    def generate_widget(self):
        return self.checkbox

    def load_val(self, value):
        self.checkbox.setChecked(value)

    def save_val(self):
        return self.checkbox.isChecked()


class LineEdit(LCV):
    view_id = 'wdcd.line_edit'
    view_name = '单行文本框'

    def __init__(self, config, container):
        super(LineEdit, self).__init__(config, container)
        self.content = QLineEdit()
        if 'placeholder' in config:
            config.setPlaceholderText(config['placeholder'])

    def load_val(self, value):
        self.content.setText(value)

    def save_val(self):
        return self.content.text()


class ComboBox(LCV):
    view_id = 'wdcd.combo_box'
    view_name = '下拉框'

    def __init__(self, config, container):
        super(ComboBox, self).__init__(config, container)
        self.content = QComboBox()
        self.content.addItems(config['items'])

    def load_val(self, value):
        self.content.setCurrentIndex(value)

    def save_val(self):
        return self.content.currentIndex()


class ColorPicker(LCV):
    view_id = 'wdcd.color_picker'
    view_name = '选色器'

    def __init__(self, config, container):
        super(ColorPicker, self).__init__(config, container)
        self.color = QColor()
        self.content = QPushButton()
        self.content.released.connect()

    def load_val(self, value):
        self.content.setText(value)

    def save_val(self):
        return self.content.text()

    def set_color(self):
        self.content.setText(QColorDialog.getColor(QColor(self.content.text())).name())


class SpinBox(LCV):
    view_id = 'wdcd.spin_box'
    view_name = '数值框'

    def __init__(self, config, container):
        super(SpinBox, self).__init__(config, container)
        if config['type'] == 'int':
            self.content = QSpinBox()
        else:
            self.content = QDoubleSpinBox()
        self.content.setMaximum(config['max'])
        self.content.setMinimum(config['min'])
        if 'suffix' in config:
            self.content.setSuffix(config['suffix'])
        if 'prefix' in config:
            self.content.setPrefix(config['prefix'])
        if 'step' in config:
            self.content.setSingleStep(config['step'])

    def load_val(self, value):
        self.content.setValue(value)

    def save_val(self):
        return self.content.value()