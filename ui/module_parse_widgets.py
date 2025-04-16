from typing import List, Callable
import time

from modules import GET_VALID_INPAINTERS, GET_VALID_TEXTDETECTORS, GET_VALID_TRANSLATORS, GET_VALID_OCR, \
    BaseTranslator, DEFAULT_DEVICE, GPUINTENSIVE_SET
from utils.logger import logger as LOGGER
from .custom_widget import ConfigComboBox, ParamComboBox, NoBorderPushBtn, ParamNameLabel
from utils.shared import CONFIG_COMBOBOX_LONG, size2width, CONFIG_COMBOBOX_SHORT, CONFIG_COMBOBOX_HEIGHT
from utils.config import pcfg
from utils.translator_test import test_translator
from utils import create_error_dialog, create_info_dialog

from qtpy.QtWidgets import QPlainTextEdit, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QCheckBox, QLineEdit, QGridLayout, QPushButton, QFrame, QSizePolicy
from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QDoubleValidator, QColor, QPalette


class ParamCheckGroup(QWidget):

    paramwidget_edited = Signal(str, dict)

    def __init__(self, param_key, check_group: dict, parent=None) -> None:
        super().__init__(parent=parent)
        self.param_key = param_key
        layout = QHBoxLayout(self)
        self.label2widget = {}
        for k, v in check_group.items():
            checker = QCheckBox(text=k, parent=self)
            checker.setChecked(v)
            layout.addWidget(checker)
            self.label2widget[k] = checker
            checker.clicked.connect(self.on_checker_clicked)

    def on_checker_clicked(self):
        new_state_dict = {}
        w = QCheckBox()
        for k, w in self.label2widget.items():
            new_state_dict[k] = w.isChecked()
        self.paramwidget_edited.emit(self.param_key, new_state_dict)


class ParamLineEditor(QLineEdit):

    paramwidget_edited = Signal(str, str)
    def __init__(self, param_key: str, force_digital, size='short', *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)
        self.param_key = param_key
        self.setFixedWidth(size2width(size))
        self.setFixedHeight(CONFIG_COMBOBOX_HEIGHT)
        self.textChanged.connect(self.on_text_changed)

        if force_digital:
            validator = QDoubleValidator()
            self.setValidator(validator)

    def on_text_changed(self):
        self.paramwidget_edited.emit(self.param_key, self.text())

class ParamEditor(QPlainTextEdit):

    paramwidget_edited = Signal(str, str)
    def __init__(self, param_key: str, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)
        self.param_key = param_key

        if param_key == 'chat sample':
            self.setFixedWidth(int(CONFIG_COMBOBOX_LONG * 1.2))
            self.setFixedHeight(200)
        else:
            self.setFixedWidth(CONFIG_COMBOBOX_LONG)
            self.setFixedHeight(100)
        # self.setFixedHeight(CONFIG_COMBOBOX_HEIGHT)
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        self.paramwidget_edited.emit(self.param_key, self.text())

    def setText(self, text: str):
        self.setPlainText(text)

    def text(self):
        return self.toPlainText()


class ParamCheckerBox(QWidget):
    checker_changed = Signal(bool)
    paramwidget_edited = Signal(str, str)
    def __init__(self, param_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_key = param_key
        self.checker = QCheckBox()
        name_label = ParamNameLabel(param_key)
        hlayout = QHBoxLayout(self)
        hlayout.addWidget(name_label)
        hlayout.addWidget(self.checker)
        hlayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.checker.stateChanged.connect(self.on_checker_changed)

    def on_checker_changed(self):
        is_checked = self.checker.isChecked()
        self.checker_changed.emit(is_checked)
        checked = 'true' if is_checked else 'false'
        self.paramwidget_edited.emit(self.param_key, checked)


class ParamCheckBox(QCheckBox):
    paramwidget_edited = Signal(str, bool)
    def __init__(self, param_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_key = param_key
        self.stateChanged.connect(self.on_checker_changed)

    def on_checker_changed(self):
        self.paramwidget_edited.emit(self.param_key, self.isChecked())


def get_param_display_name(param_key: str, param_dict: dict = None):
    if param_dict is not None and isinstance(param_dict, dict):
        if 'display_name' in param_dict:
            return param_dict['display_name']
    return param_key


class ParamPushButton(QPushButton):
    paramwidget_edited = Signal(str, str)
    def __init__(self, param_key: str, param_dict: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param_key = param_key
        self.setText(get_param_display_name(param_key, param_dict))
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.paramwidget_edited.emit(self.param_key, '')


class ParamWidget(QWidget):

    paramwidget_edited = Signal(str, dict)
    def __init__(self, params, scrollWidget: QWidget = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QHBoxLayout(self)
        self.param_layout = param_layout = QGridLayout()
        param_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(param_layout)
        layout.addStretch(-1)

        if 'description' in params:
            self.setToolTip(params['description'])

        for ii, param_key in enumerate(params):
            if param_key == 'description':
                continue
            display_param_name = param_key

            require_label = True
            is_str = isinstance(params[param_key], str)
            is_digital = isinstance(params[param_key], float) or isinstance(params[param_key], int)
            param_widget = None

            if isinstance(params[param_key], bool):
                param_widget = ParamCheckBox(param_key)
                val = params[param_key]
                param_widget.setChecked(val)
                param_widget.paramwidget_edited.connect(self.on_paramwidget_edited)

            elif is_str or is_digital:
                param_widget = ParamLineEditor(param_key, force_digital=is_digital)
                val = params[param_key]
                if is_digital:
                    val = str(val)
                param_widget.setText(val)
                param_widget.paramwidget_edited.connect(self.on_paramwidget_edited)

            elif isinstance(params[param_key], dict):
                param_dict = params[param_key]
                display_param_name = get_param_display_name(param_key, param_dict)
                value = params[param_key]['value']
                param_widget = None  # Ensure initialization
                param_type = param_dict['type'] if 'type' in param_dict else 'line_editor'
                flush_btn = param_dict.get('flush_btn', False)
                path_selector = param_dict.get('path_selector', False)
                param_size = param_dict.get('size', 'short')
                if param_type == 'selector':
                    if 'url' in param_key:
                        size = size2width('median')
                    else:
                        size = size2width(param_size)

                    param_widget = ParamComboBox(
                        param_key, param_dict['options'], size=size, scrollWidget=scrollWidget, flush_btn=flush_btn, path_selector=path_selector)

                    if param_key == 'device' and DEFAULT_DEVICE == 'cpu':
                        param_dict['value'] = 'cpu'
                        for ii, device in enumerate(param_dict['options']):
                            if device in GPUINTENSIVE_SET:
                                model = param_widget.model()
                                item = model.item(ii, 0)
                                item.setEnabled(False)
                    param_widget.setCurrentText(str(value))
                    param_widget.setEditable(param_dict.get('editable', False))

                elif param_type == 'editor':
                    param_widget = ParamEditor(param_key)
                    param_widget.setText(value)

                elif param_type == 'checkbox':
                    param_widget = ParamCheckBox(param_key)
                    if isinstance(value, str):
                        value = value.lower().strip() == 'true'
                        params[param_key]['value'] = value
                    param_widget.setChecked(value)

                elif param_type == 'pushbtn':
                    param_widget = ParamPushButton(param_key, param_dict)
                    require_label = False

                elif param_type == 'line_editor':
                    param_widget = ParamLineEditor(param_key, force_digital=is_digital)
                    param_widget.setText(str(value))

                elif param_type == 'check_group':
                    param_widget = ParamCheckGroup(param_key, check_group=value)

                if param_widget is not None:
                    param_widget.paramwidget_edited.connect(self.on_paramwidget_edited)
                    if 'description' in param_dict:
                        param_widget.setToolTip(param_dict['description'])

            widget_idx = 0
            if require_label:
                param_label = ParamNameLabel(display_param_name)
                param_layout.addWidget(param_label, ii, 0)
                widget_idx = 1
            if param_widget:
                pw_lo = None
                if hasattr(param_widget, 'flush_btn') or hasattr(param_widget, 'path_select_btn'):
                    pw_lo = QHBoxLayout()
                    pw_lo.addWidget(param_widget)
                if hasattr(param_widget, 'flush_btn'):
                    pw_lo.addWidget(param_widget.flush_btn)
                    param_widget.flushbtn_clicked.connect(self.on_flushbtn_clicked)
                if hasattr(param_widget, 'path_select_btn'):
                    pw_lo.addWidget(param_widget.path_select_btn)
                    param_widget.pathbtn_clicked.connect(self.on_pathbtn_clicked)
                if pw_lo is None:
                    param_layout.addWidget(param_widget, ii, widget_idx)
                else:
                    param_layout.addLayout(pw_lo, ii, widget_idx)
            else:
                raise ValueError(f"Failed to initialize widget for key: {param_key}")

    def on_flushbtn_clicked(self):
        paramw: ParamComboBox = self.sender()
        content_dict = {'content': '', 'widget': paramw, 'flush': True}
        self.paramwidget_edited.emit(paramw.param_key, content_dict)

    def on_pathbtn_clicked(self):
        paramw: ParamComboBox = self.sender()
        content_dict = {'content': '', 'widget': paramw, 'select_path': True}
        self.paramwidget_edited.emit(paramw.param_key, content_dict)

    def on_paramwidget_edited(self, param_key, param_content):
        content_dict = {'content': param_content}
        self.paramwidget_edited.emit(param_key, content_dict)

class ModuleParseWidgets(QWidget):
    def addModulesParamWidgets(self, ocr_instance):
        self.params = ocr_instance.get_params()
        self.on_module_changed()

    def on_module_changed(self):
        self.updateModuleParamWidget()

    def updateModuleParamWidget(self):
        widget = ParamWidget(self.params, scrollWidget=self)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)

class ModuleConfigParseWidget(QWidget):
    module_changed = Signal(str)
    paramwidget_edited = Signal(str, dict)
    def __init__(self, module_name: str, get_valid_module_keys: Callable, scrollWidget: QWidget, add_from: int = 1, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)
        self.get_valid_module_keys = get_valid_module_keys
        self.module_combobox = ConfigComboBox(scrollWidget=scrollWidget)
        self.params_layout = QHBoxLayout()
        self.params_layout.setContentsMargins(0, 0, 0, 0)

        p_layout = QHBoxLayout()
        p_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.module_label = ParamNameLabel(module_name)
        p_layout.addWidget(self.module_label)
        p_layout.addWidget(self.module_combobox)
        p_layout.addStretch(-1)
        self.p_layout = p_layout

        layout = QVBoxLayout(self)
        self.param_widget_map = {}
        layout.addLayout(p_layout)
        layout.addLayout(self.params_layout)
        layout.setSpacing(30)
        self.vlayout = layout

        self.visibleWidget: QWidget = None
        self.module_dict: dict = {}

    def addModulesParamWidgets(self, module_dict: dict):
        invalid_module_keys = []
        valid_modulekeys = self.get_valid_module_keys()

        num_widgets_before = len(self.param_widget_map)

        for module in module_dict:
            if module not in valid_modulekeys:
                invalid_module_keys.append(module)
                continue

            if module in self.param_widget_map:
                LOGGER.warning(f'duplicated module key: {module}')
                continue

            self.module_combobox.addItem(module)
            params = module_dict[module]
            if params is not None:
                self.param_widget_map[module] = None

        if len(invalid_module_keys) > 0:
            LOGGER.warning(F'Invalid module keys: {invalid_module_keys}')
            for ik in invalid_module_keys:
                module_dict.pop(ik)

        self.module_dict = module_dict

        num_widgets_after = len(self.param_widget_map)
        if num_widgets_before == 0 and num_widgets_after > 0:
            self.on_module_changed()
            self.module_combobox.currentTextChanged.connect(self.on_module_changed)

    def setModule(self, module: str):
        self.blockSignals(True)
        self.module_combobox.setCurrentText(module)
        self.updateModuleParamWidget()
        self.blockSignals(False)

    def updateModuleParamWidget(self):
        module = self.module_combobox.currentText()
        if self.visibleWidget is not None:
            self.visibleWidget.hide()
        if module in self.param_widget_map:
            widget: QWidget = self.param_widget_map[module]
            if widget is None:
                # lazy load widgets
                params = self.module_dict[module]
                widget = ParamWidget(params, scrollWidget=self)
                widget.paramwidget_edited.connect(self.paramwidget_edited)
                self.param_widget_map[module] = widget
                self.params_layout.addWidget(widget)
            else:
                widget.show()
            self.visibleWidget = widget

    def on_module_changed(self):
        self.updateModuleParamWidget()
        module_name = self.module_combobox.currentText()
        self.module_changed.emit(module_name)

        # 如果是OCRConfigPanel实例，更新current_ocr
        if hasattr(self, 'current_ocr'):
            from modules import OCR
            self.current_ocr = OCR.get(module_name)


class TranslatorConfigPanel(ModuleConfigParseWidget):

    show_pre_MT_keyword_window = Signal()
    show_MT_keyword_window = Signal()
    show_OCR_keyword_window = Signal()
    test_translator_signal = Signal()

    def __init__(self, module_name, scrollWidget: QWidget = None, *args, **kwargs) -> None:
        super().__init__(module_name, GET_VALID_TRANSLATORS, scrollWidget=scrollWidget, *args, **kwargs)
        self.translator_changed = self.module_changed
        self.current_translator = None
        self.last_test_time = 0  # 上次测试时间，用于防止连续点击

        # 连接翻译器下拉框变化信号，清除测试结果
        self.module_combobox.currentTextChanged.connect(self.onTranslatorChanged)

        # 初始化测试文本
        self.test_source_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."

        self.source_combobox = ConfigComboBox(scrollWidget=scrollWidget)
        self.target_combobox = ConfigComboBox(scrollWidget=scrollWidget)
        self.replacePreMTkeywordBtn = NoBorderPushBtn(self.tr("Keyword substitution for machine translation source text"), self)
        self.replacePreMTkeywordBtn.clicked.connect(self.show_pre_MT_keyword_window)
        self.replacePreMTkeywordBtn.setFixedWidth(500)
        self.replaceMTkeywordBtn = NoBorderPushBtn(self.tr("Keyword substitution for machine translation"), self)
        self.replaceMTkeywordBtn.clicked.connect(self.show_MT_keyword_window)
        self.replaceMTkeywordBtn.setFixedWidth(500)
        self.replaceOCRkeywordBtn = NoBorderPushBtn(self.tr("Keyword substitution for source text"), self)
        self.replaceOCRkeywordBtn.clicked.connect(self.show_OCR_keyword_window)
        self.replaceOCRkeywordBtn.setFixedWidth(500)

        # 添加测试翻译按钮
        self.testTranslatorBtn = QPushButton(self.tr("测试翻译"), self)
        self.testTranslatorBtn.clicked.connect(self.on_test_translator)
        self.testTranslatorBtn.setFixedSize(100, 30)  # 调整按钮大小
        self.testTranslatorBtn.setStyleSheet("""
            QPushButton {
                background-color: #d64541;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)

        # 添加测试结果显示区域 - 修改为垂直布局，始终显示
        self.test_result_frame = QFrame(self)
        self.test_result_frame.setFrameShape(QFrame.Shape.NoFrame)  # 无边框
        self.test_result_frame.setVisible(True)  # 始终可见
        # self.test_result_frame.setStyleSheet("border-bottom: 2px solid #008080; padding-bottom: 10px; margin-bottom: 10px;")

        test_result_layout = QVBoxLayout(self.test_result_frame)
        test_result_layout.setContentsMargins(0, 3, 0, 3)  # 进一步减小上下边距
        test_result_layout.setSpacing(4)  # 进一步减小间距

        # 源文本显示 - 垂直布局
        source_frame = QFrame()
        source_frame.setFrameShape(QFrame.Shape.NoFrame)  # 不使用框架样式
        source_frame.setStyleSheet("border-bottom: 1px solid #008080; padding-bottom: 3px;")
        source_layout = QHBoxLayout(source_frame)
        source_layout.setContentsMargins(0, 0, 0, 3)  # 减小内边距

        source_label = QLabel(self.tr("原文："))
        source_label.setFixedWidth(40)  # 减小宽度
        source_label.setStyleSheet("font-weight: bold; color: #34495e;")
        source_layout.addWidget(source_label)

        self.source_text_label = QLabel()
        self.source_text_label.setStyleSheet("color: #2c3e50;")
        self.source_text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        source_layout.addWidget(self.source_text_label)
        test_result_layout.addWidget(source_frame)

        # 移除分隔线，因为我们现在给每个组件都添加了下边框

        # 翻译结果显示 - 垂直布局
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.Shape.NoFrame)  # 不使用框架样式
        result_frame.setStyleSheet("border-bottom: 1px solid #008080; padding-bottom: 3px;")
        result_layout = QHBoxLayout(result_frame)
        result_layout.setContentsMargins(0, 0, 0, 3)  # 减小内边距

        result_label = QLabel(self.tr("译文："))
        result_label.setFixedWidth(40)  # 减小宽度
        result_label.setStyleSheet("font-weight: bold; color: #34495e;")
        result_layout.addWidget(result_label)

        self.result_text_label = QLabel()
        self.result_text_label.setStyleSheet("color: #27ae60;")
        self.result_text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        result_layout.addWidget(self.result_text_label)
        test_result_layout.addWidget(result_frame)

        # 添加测试结果和用时显示
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.NoFrame)  # 不使用框架样式
        status_frame.setStyleSheet("border-bottom: 1px solid #008080; padding-bottom: 3px;")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(60, 2, 0, 3)  # 左边留出与标签对齐的空间，减小上边距
        status_layout.setSpacing(2)  # 减小间距

        self.test_status_label = QLabel()
        self.test_status_label.setStyleSheet("color: #008080; font-size: 12px;")
        status_layout.addWidget(self.test_status_label)
        status_layout.addStretch(1)  # 添加弹性空间使用时显示在右边

        self.test_time_label = QLabel()
        self.test_time_label.setStyleSheet("color: #008080; font-size: 12px;")
        status_layout.addWidget(self.test_time_label)

        test_result_layout.addWidget(status_frame)

        st_layout = QHBoxLayout()
        st_layout.setSpacing(15)
        st_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        st_layout.addWidget(ParamNameLabel(self.tr('Source')))
        st_layout.addWidget(self.source_combobox)
        st_layout.addWidget(ParamNameLabel(self.tr('Target')))
        st_layout.addWidget(self.target_combobox)
        st_layout.addWidget(self.testTranslatorBtn)

        self.vlayout.insertLayout(1, st_layout)
        # 将测试结果区域放在源语言选择下方，low vram mode设置之上
        self.vlayout.insertWidget(2, self.test_result_frame)  # 添加测试结果显示区域
        self.vlayout.addWidget(self.replaceOCRkeywordBtn)
        self.vlayout.addWidget(self.replacePreMTkeywordBtn)
        self.vlayout.addWidget(self.replaceMTkeywordBtn)

        # 调整测试结果显示区域的位置
        self.vlayout.setAlignment(self.test_result_frame, Qt.AlignmentFlag.AlignLeft)

        # 连接源语言和目标语言下拉框变化信号，清除测试结果
        self.source_combobox.currentTextChanged.connect(self.onLanguageChanged)
        self.target_combobox.currentTextChanged.connect(self.onLanguageChanged)

    def finishSetTranslator(self, translator: BaseTranslator):
        self.source_combobox.blockSignals(True)
        self.target_combobox.blockSignals(True)
        self.module_combobox.blockSignals(True)

        self.source_combobox.clear()
        self.target_combobox.clear()

        self.source_combobox.addItems(translator.supported_src_list)
        self.target_combobox.addItems(translator.supported_tgt_list)
        self.module_combobox.setCurrentText(translator.name)
        self.source_combobox.setCurrentText(translator.lang_source)
        self.target_combobox.setCurrentText(translator.lang_target)
        self.updateModuleParamWidget()
        self.source_combobox.blockSignals(False)
        self.target_combobox.blockSignals(False)
        self.module_combobox.blockSignals(False)

        # 保存当前翻译器实例，用于测试
        self.current_translator = translator

        # 更新测试文本
        self.updateTestSourceText()
        # 显示测试源文本
        self.source_text_label.setText(self.test_source_text)

        # 清除之前的测试结果
        self.clearTestResults()

    def on_test_translator(self):
        """测试当前翻译器是否可用"""
        # 防止连续点击，限制最少3秒才能再次测试
        current_time = time.time()
        if current_time - self.last_test_time < 3:
            return
        self.last_test_time = current_time

        # 清除之前的测试结果和用时
        self.test_status_label.setText("")
        self.test_time_label.setText("")

        # 禁用按钮，防止重复点击
        self.testTranslatorBtn.setEnabled(False)
        self.testTranslatorBtn.setText(self.tr("测试中..."))

        # 创建定时器，在测试完成后重新启用按钮
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._do_test_translator(timer))
        timer.start(100)  # 延迟100毫秒执行，让UI有时间更新

    def updateTestSourceText(self):
        """根据当前翻译器的源语言更新测试文本"""
        try:
            if not self.current_translator:
                self.test_source_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."
                return

            # 获取当前选择的源语言，而不是翻译器的默认源语言
            current_source_lang = self.source_combobox.currentText()

            # 根据源语言获取测试文本
            if current_source_lang == '日本語':
                self.test_source_text = "気泡翻訳はオープンソースで無料、深層学習技術に基づく漫画翻訳ツールです。"
            elif current_source_lang == 'English':
                self.test_source_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."
            elif current_source_lang == '简体中文':
                self.test_source_text = "气泡翻译是一个开源免费,基于深度学习技术的漫画翻译工具."
            elif current_source_lang == '繁體中文':
                self.test_source_text = "氣泡翻譯是一個開源免費,基於深度學習技術的漫畫翻譯工具."
            elif current_source_lang == '한국어':
                self.test_source_text = "말풍선 번역은 오픈 소스, 무료, 딥러닝 기술 기반의 만화 번역 도구입니다."
            else:
                # 默认使用英文
                self.test_source_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."

            # 更新显示
            self.source_text_label.setText(self.test_source_text)
        except Exception as e:
            LOGGER.error(f"获取测试文本失败: {str(e)}")
            self.test_source_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."
            self.source_text_label.setText(self.test_source_text)

    def clearTestResults(self):
        """清除测试结果"""
        self.result_text_label.setText("")
        self.test_status_label.setText("")
        self.test_time_label.setText("")
        self.result_text_label.setStyleSheet("color: #27ae60;")

    def onTranslatorChanged(self, translator_name):
        """翻译器变化时清除测试结果"""
        self.clearTestResults()

    def onLanguageChanged(self, language):
        """源语言或目标语言变化时清除测试结果"""
        self.clearTestResults()
        # 更新测试文本
        self.updateTestSourceText()

    def _do_test_translator(self, timer):
        """实际执行翻译测试"""
        try:
            if not self.current_translator:
                # 显示错误信息
                self.source_text_label.setText("未选择翻译器")
                self.result_text_label.setText("请先选择翻译器")
                self.result_text_label.setStyleSheet("color: #c0392b;")
                create_error_dialog(Exception("未设置翻译器"))
                return

            # 记录开始时间
            start_time = time.time()

            # 更新测试文本
            self.updateTestSourceText()

            # 执行翻译测试
            try:
                success, _, result = test_translator(self.current_translator)

                # 计算用时
                elapsed_time = time.time() - start_time
                self.test_time_label.setText(f"用时: {elapsed_time:.2f}s")

                # 根据测试结果显示不同的提示
                if success:
                    # 成功时显示翻译结果，并设置为绿色
                    self.result_text_label.setText(result)
                    self.result_text_label.setStyleSheet("color: #27ae60;")
                    self.test_status_label.setText("测试成功")
                    self.test_status_label.setStyleSheet("color: #008080; font-size: 12px; font-weight: bold;")
                else:
                    # 失败时显示错误消息，并设置为红色
                    self.result_text_label.setText(result)
                    self.result_text_label.setStyleSheet("color: #c0392b;")
                    self.test_status_label.setText("测试失败")
                    self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold;")
            except Exception as e:
                # 翻译过程中出现异常，显示错误信息
                elapsed_time = time.time() - start_time
                self.test_time_label.setText(f"用时: {elapsed_time:.2f}s")

                error_msg = str(e)
                self.result_text_label.setText(f"翻译失败: {error_msg}")
                self.result_text_label.setStyleSheet("color: #c0392b;")
                self.test_status_label.setText("测试失败")
                self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold;")

        except Exception as e:
            # 全局异常处理
            self.source_text_label.setText("测试文本加载失败")
            self.result_text_label.setText(f"测试过程出错: {str(e)}")
            self.result_text_label.setStyleSheet("color: #c0392b;")
            self.test_status_label.setText("测试失败")
            self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold;")
        finally:
            # 恢复按钮状态
            self.testTranslatorBtn.setEnabled(True)
            self.testTranslatorBtn.setText(self.tr("测试翻译"))

            # 删除定时器
            if timer and timer.isActive():
                timer.stop()
                timer.deleteLater()


class InpaintConfigPanel(ModuleConfigParseWidget):
    def __init__(self, module_name: str, scrollWidget: QWidget = None, *args, **kwargs) -> None:
        super().__init__(module_name, GET_VALID_INPAINTERS, scrollWidget = scrollWidget, *args, **kwargs)
        self.inpainter_changed = self.module_changed
        self.setInpainter = self.setModule
        self.needInpaintChecker = ParamCheckerBox(self.tr('Let the program decide whether it is necessary to use the selected inpaint method.'))
        self.vlayout.addWidget(self.needInpaintChecker)

    def showEvent(self, e) -> None:
        self.p_layout.insertWidget(1, self.module_combobox)
        super().showEvent(e)

    def hideEvent(self, e) -> None:
        self.p_layout.removeWidget(self.module_combobox)
        return super().hideEvent(e)

class TextDetectConfigPanel(ModuleConfigParseWidget):
    def __init__(self, module_name: str, scrollWidget: QWidget = None, *args, **kwargs) -> None:
        super().__init__(module_name, GET_VALID_TEXTDETECTORS, scrollWidget = scrollWidget, *args, **kwargs)
        self.detector_changed = self.module_changed
        self.setDetector = self.setModule
        self.keep_existing_checker = QCheckBox(text=self.tr('Keep Existing Lines'))
        self.p_layout.insertWidget(2, self.keep_existing_checker)


class OCRConfigPanel(ModuleConfigParseWidget):
    def __init__(self, module_name: str, scrollWidget: QWidget = None, *args, **kwargs) -> None:
        super().__init__(module_name, GET_VALID_OCR, scrollWidget = scrollWidget, *args, **kwargs)
        self.ocr_changed = self.module_changed
        self.setOCR = self.setModule
        self.current_ocr = None

        # 添加测试OCR按钮 - 暂时隐藏
        # self.testOCRBtn = QPushButton(self.tr("测试OCR"), self)
        # self.testOCRBtn.clicked.connect(self.on_test_ocr)
        # self.testOCRBtn.setFixedSize(100, 30)  # 调整按钮大小
        # self.testOCRBtn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #008080;
        #         color: white;
        #         font-weight: bold;
        #         border-radius: 4px;
        #         padding: 2px;
        #     }
        #     QPushButton:hover {
        #         background-color: #00A3A3;
        #     }
        #     QPushButton:pressed {
        #         background-color: #006666;
        #     }
        #     QPushButton:disabled {
        #         background-color: #bdc3c7;
        #         color: #7f8c8d;
        #     }
        # """)

        # # 添加按钮到布局
        # ocr_test_layout = QHBoxLayout()
        # ocr_test_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # ocr_test_layout.addWidget(self.testOCRBtn)
        # self.vlayout.insertLayout(1, ocr_test_layout)

        # 添加恢复空OCR区域的选项
        self.restoreEmptyOCRChecker = QCheckBox(self.tr("Delete and restore region where OCR return empty string."), self)
        self.restoreEmptyOCRChecker.clicked.connect(self.on_restore_empty_ocr)
        self.vlayout.addWidget(self.restoreEmptyOCRChecker)

        # 连接OCR选择变化信号
        self.module_combobox.currentTextChanged.connect(self.on_ocr_changed)

    def on_restore_empty_ocr(self):
        pcfg.restore_ocr_empty = self.restoreEmptyOCRChecker.isChecked()

    def on_ocr_changed(self):
        """OCR变化时更新当前OCR模块"""
        ocr_name = self.module_combobox.currentText()
        from modules import OCR
        ocr_class = OCR.get(ocr_name)
        # 创建OCR模块实例
        self.current_ocr = ocr_class()
        # 加载模型
        if hasattr(self.current_ocr, '_load_model'):
            self.current_ocr._load_model()

    def on_test_ocr(self):
        """测试当前OCR模块"""
        if not self.current_ocr:
            ocr_name = self.module_combobox.currentText()
            from modules import OCR
            ocr_class = OCR.get(ocr_name)
            # 创建OCR模块实例
            self.current_ocr = ocr_class()
            # 加载模型
            if hasattr(self.current_ocr, '_load_model'):
                self.current_ocr._load_model()

        if self.current_ocr:
            # 导入OCR测试对话框
            from ui.ocr_test_dialog import OCRTestDialog
            dialog = OCRTestDialog(self.current_ocr, self)
            dialog.exec()