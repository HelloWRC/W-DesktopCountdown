from UIFrames.ui_effect_configure import Ui_Configure
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox
from PyQt5.Qt import QApplication, Qt
import logging
import properties
from data import effects


class UniverseConfigure(QWidget):
    def __init__(self, config, config_temple):
        super(UniverseConfigure, self).__init__()
        self.ui = Ui_Configure()
        self.ui.setupUi(self)
        self.config_temple = config_temple
        self.config = config
        self.gen_ui = {}
        self.set_val = {}
        self.get_val = {}

        # Generate UI
        for i in self.config_temple:
            root = self.config_temple[i]
            if root['type'] == 'label':
                label = QLabel(root['text'])
                if 'word_warp' in root:
                    label.setWordWrap(root['word_warp'])
                if 'selectable' in root:
                    if root['selectable']:
                        label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
                self.ui.container.addRow(label)
            elif root['type'] == 'bool':
                checkbox = QCheckBox(root['name'])
                checkbox.setObjectName('cb_' + i)
                if 'description' in root:
                    checkbox.setToolTip(root['description'])
                self.ui.container.addRow(checkbox)
                self.gen_ui['cb_' + i] = checkbox
                self.set_val[i] = checkbox.setChecked
                self.get_val[i] = checkbox.isChecked
            else:
                label = QLabel(root['name'])
                if 'description' in root:
                    label.setToolTip(root['description'])

                content = None
                # content
                if root['type'] == 'string':
                    content = QLineEdit()
                    content.setObjectName('le_' + i)
                    if 'placeholder' in root:
                        content.setPlaceholderText(root['placeholder'])
                    self.gen_ui['le_' + i] = content
                    self.set_val[i] = content.setText
                    self.get_val[i] = content.text
                elif root['type'] == 'int' or root['type'] == 'float':
                    if root['type'] == 'int':
                        content = QSpinBox()
                    else:
                        content = QDoubleSpinBox()
                    content.setObjectName('sb_' + i)
                    content.setMaximum(root['max'])
                    content.setMinimum(root['min'])
                    if 'suffix' in root:
                        content.setSuffix(root['suffix'])
                    if 'prefix' in root:
                        content.setPrefix(root['prefix'])
                    if 'step' in root:
                        content.setSingleStep(root['step'])
                    self.gen_ui['sb_' + i] = content
                    self.set_val[i] = content.setValue
                    self.get_val[i] = content.value
                elif root['type'] == 'combo_box':
                    content = QComboBox()
                    content.setObjectName('cb_' + i)
                    content.addItems(root['items'])
                    self.gen_ui['cb_' + i] = content
                    self.set_val[i] = content.setCurrentIndex
                    self.get_val[i] = content.currentIndex
                else:
                    continue
                if 'description' in root:
                    content.setToolTip(root['description'])
                self.ui.container.addRow(label, content)

        self.load_val()

    def load_val(self):
        for i in self.config_temple:
            if i not in self.config:
                if self.config_temple[i]['type'] == 'label':
                    continue
                self.config[i] = self.config_temple[i]['default']
            self.set_val[i](self.config[i])

    def save_val(self):
        for i in self.config_temple:
            if self.config_temple[i]['type'] == 'label':
                continue
            self.config[i] = self.get_val[i]()

    def on_btn_confirm_released(self):
        self.save_val()
        self.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=properties.log_styles,
                        datefmt=properties.datefmt,
                        filemode='w',
                        filename='latest.log')
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', properties.version)
    app = QApplication([])
    config = {}
    effect_config = UniverseConfigure(config, effects.SampleEffect.default_config)
    effect_config.show()
    app.exec_()
    print(config)
