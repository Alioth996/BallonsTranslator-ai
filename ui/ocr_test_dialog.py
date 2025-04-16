import time
import numpy as np
import cv2
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QPixmap, QImage

from utils.logger import logger as LOGGER


class OCRTestDialog(QDialog):
    """OCR测试对话框"""

    def __init__(self, ocr_module, parent=None):
        super().__init__(parent)
        self.ocr_module = ocr_module
        self.setWindowTitle("OCR测试")
        self.setFixedSize(300, 200)  # 缩小对话框大小

        # 创建测试用的示例文本图片
        self.test_image = self.create_test_image()

        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # 减小间距
        layout.setContentsMargins(5, 5, 5, 5)  # 减小边距

        # 显示测试图像
        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.Shape.StyledPanel)
        image_frame.setStyleSheet("background-color: #FFC266;")  # 橙色背景
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(3, 3, 3, 3)  # 减小内边距

        # 将NumPy数组转换为QImage并显示
        h, w, c = self.test_image.shape
        q_img = QImage(self.test_image.data, w, h, w * c, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("padding: 0px; margin: 0px;")  # 去除内边距
        image_layout.addWidget(self.image_label)

        layout.addWidget(image_frame)

        # 识别结果显示区域
        result_frame = QFrame()
        result_frame.setFrameShape(QFrame.Shape.StyledPanel)
        result_frame.setStyleSheet("background-color: #99CCFF;")  # 蓝色背景
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(3, 3, 3, 3)  # 减小内边距
        result_layout.setSpacing(2)  # 减小间距

        self.result_label = QLabel("识别结果:")
        self.result_label.setStyleSheet("color: #0066CC; font-weight: bold; font-size: 12px;")
        result_layout.addWidget(self.result_label)

        self.result_text = QLabel()
        self.result_text.setWordWrap(True)
        self.result_text.setStyleSheet("color: #0066CC; font-size: 12px;")
        self.result_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        result_layout.addWidget(self.result_text)

        # 测试用时和状态
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(2, 1, 2, 1)  # 进一步减小边距

        self.test_status_label = QLabel()
        self.test_status_label.setStyleSheet("color: #008080; font-size: 10px; font-weight: bold; text-decoration: underline;")
        status_layout.addWidget(self.test_status_label)
        status_layout.addStretch(1)

        self.test_time_label = QLabel()
        self.test_time_label.setStyleSheet("color: #008080; font-size: 10px; text-decoration: underline;")
        status_layout.addWidget(self.test_time_label)

        result_layout.addLayout(status_layout)
        layout.addWidget(result_frame)

        # 不再需要按钮区域
        # 在对话框显示后自动开始测试
        # 用户可以直接点击关闭按钮或ESC键关闭对话框

        # 创建定时器，在对话框显示后自动开始测试
        QTimer.singleShot(100, self.on_test_ocr)

    def create_test_image(self):
        """创建测试用的日文文本图像"""
        # 创建一个浅橙色背景图像
        img = np.ones((100, 280, 3), dtype=np.uint8) * 255  # 缩小图像大小
        # 设置为浅橙色背景 (RGB: 255, 204, 153)
        img[:, :, 0] = 153  # B
        img[:, :, 1] = 204  # G
        img[:, :, 2] = 255  # R

        # 添加日文文本
        # 使用PIL来绘制日文文本，因为OpenCV对非拉丁字符支持不好
        from PIL import Image, ImageDraw, ImageFont
        import os

        # 将NumPy数组转换为PIL图像
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)

        # 尝试使用系统字体
        try:
            # 尝试使用常见的日文字体
            font_path = None
            font_size = 8  # 调小字体大小以13px，以便更好地测试OCR识别能力

            # 在Windows上尝试常见的日文字体
            possible_fonts = [
                "C:\\Windows\\Fonts\\msgothic.ttc",  # MS Gothic
                "C:\\Windows\\Fonts\\YuGothR.ttc",   # Yu Gothic
                "C:\\Windows\\Fonts\\meiryo.ttc",    # Meiryo
                "C:\\Windows\\Fonts\\msmincho.ttc",  # MS Mincho
                "fonts/NotoSansJP-Regular.otf"      # 项目内字体
            ]

            for path in possible_fonts:
                if os.path.exists(path):
                    font_path = path
                    break

            if font_path:
                font = ImageFont.truetype(font_path, font_size)
                # 日文测试文本
                text = "校門の外から携てた様子でやってきた二人組の男たちに声をかけられるとちらも中年くらいで、一人はバカでかいビデオカメラのような機材を担いでいた。"

                # 将文本分成多行
                import textwrap
                lines = textwrap.wrap(text, width=30)  # 减少每行字符数，以适应更小的图像宽度

                # 绘制文本
                y_position = 15
                for line in lines:
                    draw.text((10, y_position), line, font=font, fill=(0, 0, 0))
                    y_position += font_size + 5  # 减小行间距
            else:
                # 如果找不到字体，使用默认字体
                draw.text((10, 15), "日本語テスト", fill=(0, 0, 0))
                draw.text((10, 40), "Japanese Text Test", fill=(0, 0, 0))
        except Exception as e:
            # 如果出现异常，绘制简单的提示文本
            LOGGER.error(f"绘制日文文本失败: {e}")
            draw.text((10, 15), "OCR Test Image", fill=(0, 0, 0))
            draw.text((10, 40), "日本語テスト", fill=(0, 0, 0))

        # 将PIL图像转换回 NumPy数组
        img = np.array(pil_img)

        return img

    def on_test_ocr(self):
        """测试OCR功能"""
        # 清除之前的结果
        self.result_text.setText("正在进行测试...")
        self.test_status_label.setText("")
        self.test_time_label.setText("")

        # 创建定时器，给UI一点时间更新
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._do_test_ocr(timer))
        timer.start(100)  # 延迟100毫秒执行，让UI有时间更新

    def _do_test_ocr(self, timer):
        """实际执行OCR测试"""
        try:
            if not self.ocr_module:
                self.result_text.setText("错误: OCR模块未初始化")
                self.test_status_label.setText("测试失败!")
                self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold; text-decoration: underline;")
                return

            # 记录开始时间
            start_time = time.time()

            # 执行OCR识别
            try:
                # 直接使用ocr_img方法
                result = self.ocr_module.ocr_img(self.test_image)

                # 计算用时
                elapsed_time = time.time() - start_time
                self.test_time_label.setText(f"耗时: {elapsed_time:.2f}s")

                # 显示结果
                if result and result.strip():
                    self.result_text.setText(result)
                    self.test_status_label.setText("测试成功!")
                    self.test_status_label.setStyleSheet("color: #008080; font-size: 12px; font-weight: bold; text-decoration: underline;")
                else:
                    self.result_text.setText("OCR未返回任何文本")
                    self.test_status_label.setText("测试失败!")
                    self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold; text-decoration: underline;")
            except Exception as e:
                # OCR过程中出现异常
                elapsed_time = time.time() - start_time
                self.test_time_label.setText(f"耗时: {elapsed_time:.2f}s")

                error_msg = str(e)
                self.result_text.setText(f"OCR识别失败: {error_msg}")
                self.test_status_label.setText("测试失败!")
                self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold; text-decoration: underline;")
                LOGGER.error(f"OCR测试失败: {error_msg}")

        except Exception as e:
            # 全局异常处理
            self.result_text.setText(f"测试过程出错: {str(e)}")
            self.test_status_label.setText("测试失败!")
            self.test_status_label.setStyleSheet("color: #c0392b; font-size: 12px; font-weight: bold; text-decoration: underline;")
            LOGGER.error(f"OCR测试全局异常: {str(e)}")

        finally:
            # 删除定时器
            if timer and timer.isActive():
                timer.stop()
                timer.deleteLater()
