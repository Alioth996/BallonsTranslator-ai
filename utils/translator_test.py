"""
工具类，用于测试翻译器是否可用
"""
from typing import Tuple, Optional, Dict, Any

from modules.translators.base import BaseTranslator
from modules.translators.exceptions import TranslatorSetupFailure, InvalidSourceOrTargetLanguage, TranslationNotFound
from utils.logger import logger as LOGGER

def test_translator(translator: BaseTranslator) -> Tuple[bool, str, str]:
    """
    测试翻译器是否可用

    Args:
        translator: 要测试的翻译器实例

    Returns:
        Tuple[bool, str, str]: (是否成功, 源文本, 翻译结果或错误消息)
    """
    # 首先准备测试文本，确保即使出错也能返回源文本
    try:
        # 准备测试文本 - 使用项目简介作为测试文本
        if translator.lang_source == '日本語':
            test_text = "気泡翻訳はオープンソースで無料、深層学習技術に基づく漫画翻訳ツールです。"
        elif translator.lang_source == 'English':
            test_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."
        elif translator.lang_source == '简体中文':
            test_text = "气泡翻译器是一个开源免费,基于深度学习技术的漫画翻译工具."
        elif translator.lang_source == '繁體中文':
            test_text = "氣泡翻譯器是一個開源免費,基於深度學習技術的漫畫翻譯工具."
        elif translator.lang_source == '한국어':
            test_text = "말풍선 번역은 오픈 소스, 무료, 딥러닝 기술 기반의 만화 번역 도구입니다."
        else:
            # 默认使用英文
            test_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."
    except Exception as e:
        LOGGER.error(f"获取测试文本失败: {str(e)}")
        test_text = "Balloon Translation is an open-source, free manga translation tool based on deep learning technology."

    try:
        # 执行翻译
        LOGGER.info(f"测试翻译器 {translator.name}，源语言: {translator.lang_source}，目标语言: {translator.lang_target}")
        LOGGER.info(f"测试文本: {test_text}")

        result = translator.translate(test_text)

        if not result or result == "":
            return False, test_text, "翻译结果为空，请检查翻译器设置"

        LOGGER.info(f"翻译结果: {result}")
        return True, test_text, result

    except TranslatorSetupFailure as e:
        LOGGER.error(f"翻译器设置失败: {str(e)}")
        return False, test_text, f"翻译器设置失败: {str(e)}"
    except InvalidSourceOrTargetLanguage as e:
        LOGGER.error(f"不支持的语言: {str(e)}")
        return False, test_text, f"不支持的语言: {str(e)}"
    except TranslationNotFound as e:
        LOGGER.error(f"未找到翻译: {str(e)}")
        return False, test_text, f"未找到翻译: {str(e)}"
    except Exception as e:
        LOGGER.error(f"翻译测试失败: {str(e)}")
        return False, test_text, f"翻译测试失败: {str(e)}"
