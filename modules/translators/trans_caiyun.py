from .base import *

@register_translator('Caiyun')
class CaiyunTranslator(BaseTranslator):

    concate_text = False
    cht_require_convert = True
    params: Dict = {
        'token': '',
        'delay': 0.0
    }

    def _setup_translator(self):
        self.lang_map['简体中文'] = 'zh'
        self.lang_map['繁體中文'] = 'zh'
        self.lang_map['日本語'] = 'ja'
        self.lang_map['English'] = 'en'

    def _translate(self, src_list: List[str]) -> List[str]:

        url = "https://api.interpreter.caiyunai.com/v1/translator"  # 使用https协议
        token = self.params['token']
        if token == '' or token is None:
            raise MissingTranslatorParams('token')

        direction = self.lang_map[self.lang_source] + '2' + self.lang_map[self.lang_target]

        payload = {
            "source": src_list,
            "trans_type": direction,
            "request_id": "demo_" + str(int(time.time())),
            "detect": True,
        }

        headers = {
            "Content-Type": "application/json",  # 注意大小写
            "X-Authorization": "token " + token,  # 注意大小写
        }

        try:
            # 记录请求信息
            LOGGER.info(f"彩云翻译请求: URL={url}, 方向={direction}")
            LOGGER.info(f"请求头: {headers}")
            LOGGER.info(f"请求体: {payload}")

            # 使用json参数而不是data参数
            response = requests.post(url, json=payload, headers=headers)

            # 记录响应信息
            LOGGER.info(f"彩云翻译响应状态码: {response.status_code}")
            LOGGER.info(f"彩云翻译响应内容: {response.text}")

            # 检查响应状态码
            if response.status_code != 200:
                LOGGER.error(f"彩云翻译API返回错误状态码: {response.status_code}")
                return [f"状态码: {response.status_code}, 响应: {response.text}"] * len(src_list)

            # 检查响应内容是否为空
            if not response.text.strip():
                LOGGER.error("彩云翻译API返回空响应")
                return ["空响应"] * len(src_list)

            # 解析JSON响应
            response_json = response.json()  # 使用response.json()而不json.loads(response.text)

            # 检查响应中是否包含target字段
            if "target" not in response_json:
                # 直接返回API原始响应
                LOGGER.error(f"彩云翻译API响应中缺少target字段: {response.text}")
                return [response.text] * len(src_list)

            translations = response_json["target"]
            return translations

        except json.JSONDecodeError as e:
            # 直接返回API原始响应
            LOGGER.error(f"彩云翻译响应解析错误: {str(e)}")
            LOGGER.error(f"原始响应: {response.text if 'response' in locals() else '无响应'}")
            return [response.text if 'response' in locals() else str(e)] * len(src_list)
        except requests.RequestException as e:
            # 返回请求异常信息
            LOGGER.error(f"彩云翻译请求异常: {str(e)}")
            return [str(e)] * len(src_list)
        except Exception as e:
            # 返回原始异常信息
            LOGGER.error(f"彩云翻译异常: {str(e)}")
            return [str(e)] * len(src_list)