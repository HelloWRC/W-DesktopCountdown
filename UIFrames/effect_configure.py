from UIFrames.ui_effect_configure import Ui_Configure
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox
from PyQt5.Qt import QApplication
import logging
import properties
import sys
import effects


class EffectConfigure(QWidget):
    def __init__(self, config, config_temple):
        super(EffectConfigure, self).__init__()
        self.ui = Ui_Configure()
        self.ui.setupUi(self)
        self.config_temple = config_temple
        self.config = config
        self.gen_ui = {}

        # Generate UI
        for i in self.config_temple:
            root = self.config_temple[i]
            if root['type'] == 'bool':
                checkbox = QCheckBox(root['name'])
                checkbox.setObjectName('cb_' + i)
                if 'description' in root:
                    checkbox.setToolTip(root['description'])
                self.ui.container.addRow(checkbox)
                self.gen_ui['cb_' + i] = checkbox
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
                elif root['type'] == 'combo_box':
                    content = QComboBox()
                    content.addItems(root['items'])
                else:
                    content = QLineEdit()
                    content.setEnabled(False)
                if 'description' in root:
                    content.setToolTip(root['description'])
                self.ui.container.addRow(label, content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=properties.log_styles,
                        datefmt=properties.datefmt,
                        filemode='w',
                        filename='latest.log')
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', properties.version)
    app = QApplication([])
    effect_config = EffectConfigure({}, effects.SampleEffect.default_config)
    effect_config.show()
    sys.exit(app.exec_())
