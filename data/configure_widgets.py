from abc import ABC

from functions.plugins import ConfigureView as CV
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, \
    QColorDialog, QFrame, QFormLayout, QHBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.Qt import QApplication, Qt, QSize


# Static widgets
class Label(CV):
    view_id = 'wdcd.label'
    view_name = '文字'
    can_store = False

    def __init__(self, config, container):
        self.config = config
        self.widget = QLabel(self.config['text'])
        if 'word_warp' in self.config:
            self.widget.setWordWrap(self.config['word_warp'])
        if 'selectable' in self.config:
            if self.config['selectable']:
                self.widget.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

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
    auto_set_description = True

    def __init__(self, config, container):
        self.config = config
        self.content = None
        self.label = QLabel(config['name'])
        if 'description' in config:
            self.label.setToolTip(config['description'])

    def generate_widget(self):
        if self.auto_set_description and 'description' in self.config:
            self.content.setToolTip(self.config['description'])
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
            self.content.setPlaceholderText(config['placeholder'])

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
        self.content.released.connect(self.set_color)

    def load_val(self, value):
        self.content.setText(value)
        self.content.setStyleSheet('color: {}'.format(value))

    def save_val(self):
        return self.content.text()

    def set_color(self):
        color = QColorDialog.getColor(QColor(self.content.text())).name()
        self.content.setText(color)
        self.content.setStyleSheet('color: {}'.format(color))


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


class RichTextEdit(LCV):
    view_id = 'wdcd.rich_edit'
    view_name = '富文本编辑'
    auto_set_description = False
    
    def __init__(self, config, container):
        from UIFrames.format_edit import FormatEdit
        super(RichTextEdit, self).__init__(config, container)
        self.layout = QHBoxLayout()
        self.content = self.layout
        self.line_edit = QLineEdit()
        self.button = QPushButton('...')

        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.button)

        if 'placeholder' in config:
            self.line_edit.setPlaceholderText(config['placeholder'])
        if 'description' in self.config:
            self.line_edit.setToolTip(self.config['description'])
        self.placeholders = {}
        if 'placeholders' in self.config:
            self.placeholders = self.config['placeholders']
        self.button.setToolTip('编辑富文本')
        self.editor = FormatEdit('编辑富文本', self.line_edit.setText, self.placeholders)
        self.button.released.connect(lambda: self.editor.open_edit_window(self.line_edit.text()))

    def load_val(self, value):
        self.line_edit.setText(value)

    def save_val(self):
        return self.line_edit.text()
