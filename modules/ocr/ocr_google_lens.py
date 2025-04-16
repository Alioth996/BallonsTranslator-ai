import re
import numpy as np
import time
import cv2
import random
import string
from typing import List, Dict, Any, Tuple, Optional, Union

import httpx
from PIL import Image
import io
import json5  # Используем json5 напрямую
from urllib.parse import parse_qs, urlparse
from utils.proxy_utils import create_httpx_client, normalize_proxy_url

# Убираем lxml.html и http.cookiejar, так как они больше не нужны
# import lxml.html
# import http.cookiejar as cookielib

from .base import register_OCR, OCRBase, TextBlock


class LensCore:
    LENS_UPLOAD_ENDPOINT = "https://lens.google.com/v3/upload"
    LENS_METADATA_ENDPOINT = "https://lens.google.com/qfmetadata"
    # Обновленные заголовки из нового скрипта
    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru",  # Используем 'ru' как в новом скрипте, можно сделать параметром при желании
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not-A.Brand";v="8", "Chromium";v="135", "Google Chrome";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Origin": "https://www.google.com",  # Изменено
        "Referer": "https://www.google.com/",  # Изменено
        "Sec-Fetch-Site": "same-site",  # Изменено
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",  # Добавлено
    }
    SUPPORTED_MIMES = [  # Оставляем из старого кода, хотя новый код определяет сам
        "image/x-icon",
        "image/bmp",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "image/webp",
        "image/heic",
    ]

    def __init__(self, proxy: Optional[Union[str, Dict[str, str]]] = None):
        self.proxy = proxy
        # self.cookie_jar = cookielib.CookieJar() # Убрали, httpx управляет куками внутри клиента

    @staticmethod
    def _extract_ids_from_url(url_string: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            parsed_url = urlparse(url_string)
            query_params = parse_qs(parsed_url.query)
            vsrid = query_params.get("vsrid", [None])[0]
            lsessionid = query_params.get("lsessionid", [None])[0]
            return vsrid, lsessionid
        except Exception as e:
            # Логирование можно добавить сюда при необходимости, если self.logger доступен
            print(
                f"Error extracting IDs from URL {url_string}: {e}"
            )  # Просто вывод для примера
            return None, None

    def _create_httpx_client(self) -> httpx.Client:
        """Создает httpx клиент с настройками прокси."""
        client_kwargs = {
            "follow_redirects": True,
            "timeout": httpx.Timeout(30.0, connect=10.0),
            "limits": httpx.Limits(max_keepalive_connections=5, max_connections=10),
            "http2": False,
            "verify": True,  # Можно сделать параметром, если нужно отключать проверку SSL
        }

        # 使用通用代理工具创建客户端
        return create_httpx_client(self.proxy, **client_kwargs)

    def scan_by_data(
        self, data: bytes, mime: str, dimensions: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Отправляет данные изображения в Google Lens и получает результат OCR.
        Использует двухэтапный процесс: загрузка, затем получение метаданных.
        """
        random_filename = "".join(random.choices(string.ascii_letters, k=8))
        # Определяем расширение на основе mime-типа для имени файла
        ext = ".jpg"  # По умолчанию
        if mime == "image/png":
            ext = ".png"
        elif mime == "image/webp":
            ext = ".webp"
        elif mime == "image/gif":
            ext = ".gif"
        # Добавьте другие типы при необходимости

        filename = f"{random_filename}{ext}"

        files = {"encoded_image": (filename, data, mime)}
        # Параметры для запроса загрузки из нового скрипта
        params_upload = {
            "hl": "ru",  # Язык интерфейса Lens
            "re": "av",
            "vpw": "1903",  # Используем фиксированные значения из нового скрипта
            "vph": "953",  # Вместо dimensions, как в новом скрипте
            "ep": "gsbubb",
            "st": str(int(time.time() * 1000)),
        }

        try:
            # Создаем клиент для сессии (включая обработку прокси)
            with self._create_httpx_client() as client:
                # 1. Загрузка изображения
                upload_headers = self.HEADERS.copy()
                response_upload = client.post(
                    self.LENS_UPLOAD_ENDPOINT,
                    headers=upload_headers,
                    files=files,
                    params=params_upload,
                )
                response_upload.raise_for_status()  # Проверка на HTTP ошибки

                final_url = str(response_upload.url)  # URL после редиректов

                # 2. Извлечение ID сессии
                vsrid, lsessionid = self._extract_ids_from_url(final_url)
                if not vsrid or not lsessionid:
                    raise Exception(
                        "Failed to extract vsrid or lsessionid from upload redirect URL."
                    )

                # 3. Запрос метаданных
                metadata_params = {
                    "vsrid": vsrid,
                    "lsessionid": lsessionid,
                    "hl": params_upload["hl"],
                    "qf": "CAI%3D",
                    "st": str(int(time.time() * 1000)),
                    "vpw": params_upload["vpw"],
                    "vph": params_upload["vph"],
                    "source": "lens",
                }
                # Модифицированные заголовки для запроса метаданных из нового скрипта
                metadata_headers = self.HEADERS.copy()
                metadata_headers.update(
                    {
                        "Accept": "*/*",
                        "Referer": final_url,  # Важно указать реферер
                        "Sec-Fetch-Site": "same-origin",  # Изменено
                        "Sec-Fetch-Mode": "cors",  # Изменено
                        "Sec-Fetch-Dest": "empty",  # Изменено
                        "Priority": "u=1, i",  # Изменено
                    }
                )
                # Удаляем ненужные для этого запроса заголовки
                metadata_headers.pop("Upgrade-Insecure-Requests", None)
                metadata_headers.pop("Sec-Fetch-User", None)
                metadata_headers.pop("Cache-Control", None)
                metadata_headers.pop("Origin", None)  # Origin не нужен для GET

                response_metadata = client.get(
                    self.LENS_METADATA_ENDPOINT,
                    headers=metadata_headers,
                    params=metadata_params,
                )
                response_metadata.raise_for_status()

                # 4. Парсинг ответа метаданных
                response_text = response_metadata.text
                # Убираем префикс, если он есть
                if response_text.startswith(")]}'\n"):
                    response_text = response_text[5:]
                elif response_text.startswith(")]}'"):
                    response_text = response_text[4:]

                # Используем json5 для парсинга
                metadata_json = json5.loads(response_text)
                return metadata_json  # Возвращаем распарсенный JSON

        except httpx.HTTPStatusError as e:
            # Логирование можно улучшить, передавая self.logger
            print(f"HTTP error: {e.response.status_code} for URL {e.request.url}")
            raise Exception(f"HTTP Error {e.response.status_code}") from e
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise Exception(f"Request Error: {e}") from e
        except Exception as e:
            print(f"Unexpected error in scan_by_data: {e}")
            raise  # Перевыбрасываем другие ошибки


class Lens(LensCore):
    def __init__(self, proxy: Optional[Union[str, Dict[str, str]]] = None):
        super().__init__(proxy=proxy)

    @staticmethod
    def resize_image(
        image: Image.Image, max_size: Tuple[int, int] = (1000, 1000)
    ) -> Tuple[bytes, Tuple[int, int]]:
        """Изменяет размер изображения и конвертирует в JPEG байты."""
        # Эта логика остается полезной
        image.thumbnail(max_size)
        if image.mode in ("RGBA", "P"):  # Добавим P для палитры
            image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)  # Можно настроить качество
        return buffer.getvalue(), image.size

    def scan_by_file(self, file_path: str) -> Dict[str, Any]:
        """Сканирует изображение из файла."""
        try:
            with Image.open(file_path) as img:
                img_data, dimensions = self.resize_image(img)
                # Определяем mime тип (хотя scan_by_data пока использует только имя файла)
                mime = Image.MIME.get(img.format) or "image/jpeg"
            return self.scan_by_data(img_data, mime, dimensions)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error processing image file {file_path}: {e}") from e

    def scan_by_buffer(self, buffer: bytes) -> Dict[str, Any]:
        """Сканирует изображение из байтового буфера."""
        try:
            img = Image.open(io.BytesIO(buffer))
            img_data, dimensions = self.resize_image(img)
            mime = Image.MIME.get(img.format) or "image/jpeg"
            return self.scan_by_data(img_data, mime, dimensions)
        except Exception as e:
            raise Exception(f"Error processing image buffer: {e}") from e


class LensAPI:
    def __init__(self, proxy: Optional[Union[str, Dict[str, str]]] = None):
        self.lens = Lens(proxy=proxy)

    @staticmethod
    def adaptive_parse_text_and_language(
        metadata_json: Any,
    ) -> Tuple[Optional[str], List[str], List[Dict[str, Any]]]:
        """
        Адаптивно парсит JSON для извлечения языка, текстовых блоков и аннотаций слов.
        Это синхронная версия функции из нового скрипта.
        """
        language = None
        all_word_annotations = []
        reconstructed_blocks = []

        try:
            if not isinstance(metadata_json, list) or not metadata_json:
                # Логгирование или вывод ошибки
                print("Invalid JSON structure: metadata_json is not a non-empty list.")
                return None, [], []

            response_container = next(
                (
                    item
                    for item in metadata_json
                    if isinstance(item, list)
                    and item
                    and item[0] == "fetch_query_formulation_metadata_response"
                ),
                None,
            )
            if response_container is None:
                print(
                    "Could not find 'fetch_query_formulation_metadata_response' container."
                )
                return None, [], []

            # --- Извлечение языка ---
            try:
                # Путь к языку может варьироваться, пробуем наиболее вероятный
                # Примерный путь: response_container[2] содержит список, где один из элементов - код языка 'xx'
                if len(response_container) > 2 and isinstance(
                    response_container[2], list
                ):
                    lang_section = response_container[2]
                    # Ищем строку из 2 символов
                    language = next(
                        (
                            element
                            for element in lang_section
                            if isinstance(element, str) and len(element) == 2
                        ),
                        None,
                    )
                    # Альтернативный путь, если первый не сработал (гипотетический)
                    # if not language and len(response_container) > 1 and isinstance(response_container[1], list):
                    #     lang_section = response_container[1]
                    #     language = next((element for element in lang_section if isinstance(element, str) and len(element) == 2), None)

            except (IndexError, TypeError, StopIteration):
                print("Could not find language code in expected structure.")
                pass  # Продолжаем без языка

            # --- Извлечение текста/слов ---
            segments_iterable = None
            # Пробуем разные пути к списку сегментов/блоков текста
            # Эти пути основаны на анализе JSON ответа Lens и могут потребовать корректировки
            possible_paths_to_segments_list = [
                lambda rc: (
                    rc[1][0][0][0]
                    if len(rc) > 1
                    and isinstance(rc[1], list)
                    and rc[1]
                    and isinstance(rc[1][0], list)
                    and rc[1][0]
                    and isinstance(rc[1][0][0], list)
                    and rc[1][0][0]
                    and isinstance(rc[1][0][0][0], list)
                    else None
                ),  # Самый частый путь из нового скрипта
                lambda rc: (
                    rc[2][0][0][0]
                    if len(rc) > 2
                    and isinstance(rc[2], list)
                    and rc[2]
                    and isinstance(rc[2][0], list)
                    and rc[2][0]
                    and isinstance(rc[2][0][0], list)
                    and rc[2][0][0]
                    and isinstance(rc[2][0][0][0], list)
                    else None
                ),  # Другой возможный путь
                lambda rc: (
                    rc[1][0][0]
                    if len(rc) > 1
                    and isinstance(rc[1], list)
                    and rc[1]
                    and isinstance(rc[1][0], list)
                    and rc[1][0]
                    and isinstance(rc[1][0][0], list)
                    else None
                ),  # Более короткий путь
                lambda rc: (
                    rc[2][0][0]
                    if len(rc) > 2
                    and isinstance(rc[2], list)
                    and rc[2]
                    and isinstance(rc[2][0], list)
                    and rc[2][0]
                    and isinstance(rc[2][0][0], list)
                    else None
                ),
            ]

            for path_func in possible_paths_to_segments_list:
                try:
                    candidate_iterable = path_func(response_container)
                    # Проверяем, что это не пустой список списков (сегментов)
                    if isinstance(candidate_iterable, list) and candidate_iterable:
                        # Проверяем структуру первого элемента на наличие списка слов
                        first_segment = candidate_iterable[0]
                        if (
                            isinstance(first_segment, list)
                            and len(first_segment) > 1
                            and isinstance(first_segment[1], list)
                        ):
                            # Дополнительная проверка на вложенность, характерную для списка слов
                            if (
                                first_segment[1]
                                and isinstance(first_segment[1][0], list)
                                and first_segment[1][0]
                                and isinstance(first_segment[1][0][0], list)
                            ):
                                segments_iterable = candidate_iterable
                                break  # Нашли подходящую структуру
                except (IndexError, TypeError, AttributeError):
                    continue  # Пробуем следующий путь

            if segments_iterable is None:
                print(f"Could not identify valid text segments list.")
                # Попытка найти полный текст в другом месте (как в старом коде)
                try:
                    full_text_alt = response_container[2][0][
                        0
                    ]  # Путь из старого кода data[3][4][0][0] адаптирован
                    if isinstance(full_text_alt, list):
                        reconstructed_blocks = full_text_alt
                    elif isinstance(full_text_alt, str):
                        reconstructed_blocks = [full_text_alt]
                    print("Found alternative full text structure.")
                    return (
                        language,
                        reconstructed_blocks,
                        [],
                    )  # Возвращаем без координат
                except (IndexError, TypeError):
                    print("Could not find alternative full text structure either.")
                    return language, [], []  # Ничего не найдено

            # Обработка найденных сегментов
            for segment_list in segments_iterable:
                current_block_word_annotations = []
                block_text_builder = io.StringIO()
                last_word_ends_with_space = False

                if (
                    not isinstance(segment_list, list)
                    or len(segment_list) < 2
                    or not isinstance(segment_list[1], list)
                ):
                    print(
                        f"Skipping segment: Invalid structure or word group list not found at index [1]. Segment: {segment_list}"
                    )
                    continue

                try:
                    word_groups_list = segment_list[1]

                    for group_count, word_group in enumerate(word_groups_list, 1):
                        # Ожидаемая структура: [[word_list]]
                        if not (
                            isinstance(word_group, list)
                            and len(word_group) > 0
                            and isinstance(word_group[0], list)
                        ):
                            print(
                                f"Skipping word group: Invalid structure. Group: {word_group}"
                            )
                            continue

                        word_list = word_group[0]

                        if (
                            group_count > 1
                            and block_text_builder.tell() > 0
                            and not last_word_ends_with_space
                        ):
                            block_text_builder.write(" ")
                            last_word_ends_with_space = True

                        for word_info in word_list:
                            # Ожидаемая структура слова: [?, text, space_indicator, [bbox], ...]
                            try:
                                if (
                                    isinstance(word_info, list)
                                    and len(word_info) > 3
                                    and isinstance(word_info[1], str)
                                    and isinstance(word_info[2], str)
                                    and isinstance(word_info[3], list)
                                    and word_info[3]
                                    and isinstance(word_info[3][0], list)
                                ):

                                    text = word_info[1]
                                    space_indicator = word_info[2]  # Обычно " " или ""
                                    bbox = word_info[3][
                                        0
                                    ]  # Сам bbox [[x,y], [x,y], [x,y], [x,y]] ? или [x,y,w,h] ? Проверить!
                                    # Новый парсер возвращает bbox, сохраняем его. Формат может потребовать уточнения.
                                    # Пример из нового скрипта предполагает bbox = word_info[3][0], оставляем так.

                                    current_block_word_annotations.append(
                                        {"text": text, "bbox": bbox}
                                    )

                                    block_text_builder.write(text)
                                    if (
                                        space_indicator
                                    ):  # Добавляем пробел только если он есть
                                        block_text_builder.write(space_indicator)
                                        last_word_ends_with_space = (
                                            space_indicator == " "
                                        )
                                    else:
                                        last_word_ends_with_space = False
                                else:
                                    print(
                                        f"Skipping word info: Invalid structure. Info: {word_info}"
                                    )

                            except (IndexError, TypeError):
                                print(f"Error processing word info: {word_info}")
                                continue  # К следующему слову

                except (IndexError, TypeError) as e:
                    print(f"Error processing word groups in segment: {e}")
                except Exception as e:
                    print(f"Unexpected error processing segment: {e}")

                reconstructed_text = block_text_builder.getvalue().rstrip(
                    " "
                )  # Убираем лишний пробел в конце блока
                block_text_builder.close()

                if (
                    reconstructed_text or current_block_word_annotations
                ):  # Добавляем блок если есть текст или аннотации
                    reconstructed_blocks.append(reconstructed_text)
                    all_word_annotations.extend(current_block_word_annotations)

        except Exception as e:
            print(f"Critical error during adaptive text extraction: {e}")
            # Возвращаем то, что успели собрать
            return language, reconstructed_blocks, all_word_annotations

        # print(f"Adaptive parsing complete. Lang: '{language}'. Blocks: {len(reconstructed_blocks)}. Words: {len(all_word_annotations)}.")
        return language, reconstructed_blocks, all_word_annotations

    @staticmethod
    def stitch_text_sequential(word_annotations: List[Dict[str, Any]]) -> str:
        """Просто соединяет текст из аннотаций слов."""
        # Новый парсер уже содержит space_indicator, но для совместимости сделаем просто join
        # Возможно, лучше использовать reconstructed_blocks из парсера?
        # Пока оставим так для имитации старого поведения 'Coordinate sequence'
        text = " ".join([item["text"] for item in word_annotations])
        # Применим простое удаление пробелов перед знаками препинания
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        return text.strip()

    @staticmethod
    def stitch_text_smart(word_annotations: List[Dict[str, Any]]) -> str:
        if (
            not word_annotations
            or "bbox" not in word_annotations[0]
            or not isinstance(word_annotations[0]["bbox"], list)
            or not word_annotations[0]["bbox"]
        ):
            print("Cannot perform smart stitching: bbox data missing or invalid.")
            return LensAPI.stitch_text_sequential(
                word_annotations
            )  # Возврат к простому соединению

        try:
            # Пытаемся извлечь координаты для сортировки (берем Y первой точки)
            def get_sort_key(element):
                try:
                    # Допустим bbox = [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                    bbox = element["bbox"]
                    if isinstance(bbox[0], list) and len(bbox[0]) >= 2:
                        y = bbox[0][1]  # Y координата первой точки
                        x = bbox[0][0]  # X координата первой точки
                        return (round(y, 2), x)  # Сортируем по Y, затем по X
                    # Допустим bbox = [x, y, w, h] (менее вероятно для Lens)
                    elif len(bbox) >= 2:
                        y = bbox[1]
                        x = bbox[0]
                        return (round(y, 2), x)
                    else:
                        return (0, 0)  # Не удалось извлечь
                except (IndexError, TypeError):
                    return (0, 0)  # Ошибка при извлечении

            sorted_elements = sorted(word_annotations, key=get_sort_key)

            stitched_lines = []
            current_line = []
            current_y = None
            # Порог для определения новой строки (нужно подбирать экспериментально)
            # Зависит от масштаба координат bbox
            y_threshold = 10  # Примерное значение, если координаты в пикселях

            for element in sorted_elements:
                element_y, _ = get_sort_key(element)
                text = element["text"]

                if current_y is None or abs(element_y - current_y) > y_threshold:
                    if current_line:
                        stitched_lines.append(" ".join(current_line))
                    current_line = [text]
                    current_y = element_y
                else:
                    # Простая логика склеивания знаков препинания
                    if text in [",", ".", "!", "?", ";", ":"] and current_line:
                        current_line[-1] += text
                    else:
                        current_line.append(text)

            if current_line:
                stitched_lines.append(" ".join(current_line))

            return "\n".join(stitched_lines).strip()

        except Exception as e:
            print(f"Error during smart stitching: {e}")
            return LensAPI.stitch_text_sequential(
                word_annotations
            )  # Возврат к простому

    def process_image(
        self,
        image_path: Optional[str] = None,
        image_buffer: Optional[bytes] = None,
        response_method: str = "Full Text",
    ) -> Dict[str, Any]:
        """Обрабатывает изображение и возвращает результат OCR."""
        if image_path:
            raw_result_json = self.lens.scan_by_file(image_path)
        elif image_buffer:
            raw_result_json = self.lens.scan_by_buffer(image_buffer)
        else:
            raise ValueError("Either image_path or image_buffer must be provided")

        # Парсим результат с помощью новой функции
        language, reconstructed_blocks, word_annotations = (
            self.adaptive_parse_text_and_language(raw_result_json)
        )

        # Формируем результат в зависимости от выбранного метода
        full_text = ""
        if response_method == "Full Text":
            # Используем текст, реконструированный парсером по блокам
            full_text = "\n".join(reconstructed_blocks).strip()
            if not full_text and word_annotations:  # Если блоки пустые, но слова есть
                full_text = self.stitch_text_sequential(word_annotations)

        elif response_method == "Coordinate sequence":
            # Соединяем слова последовательно
            full_text = self.stitch_text_sequential(word_annotations)

        elif response_method == "Location coordinates":
            # Пытаемся соединить умнее (или возвращаем реконструированные блоки)
            # full_text = self.stitch_text_smart(word_annotations) # Можно раскомментировать для теста
            # Пока возвращаем реконструированный текст, т.к. парсер уже пытается это делать
            full_text = "\n".join(reconstructed_blocks).strip()
            if not full_text and word_annotations:
                full_text = self.stitch_text_sequential(word_annotations)
        else:
            raise ValueError(f"Invalid response method: {response_method}")

        return {
            "full_text": (
                full_text if full_text else ""
            ),  # Возвращаем пустую строку если текста нет
            "language": language if language else "und",  # 'und' - неопределенный
            "text_with_coordinates": word_annotations,  # Возвращаем список аннотаций слов
        }


def format_ocr_result(result: Dict[str, Any]) -> str:
    """Форматирует результат OCR для вывода (например, в debug)."""
    # Адаптируем под новый формат 'text_with_coordinates' (список словарей)
    formatted_result = {
        "language": result.get("language", "und"),
        "full_text_preview": result.get("full_text", "")[:100]
        + "...",  # Добавим превью текста
        "word_annotations_count": len(result.get("text_with_coordinates", [])),
        # Выводим первые несколько аннотаций для примера
        "word_annotations_preview": [
            f"{item['text']} (bbox: {item.get('bbox', 'N/A')})"
            for item in result.get("text_with_coordinates", [])[:5]  # Первые 5 слов
        ],
    }
    try:
        # Используем json5 для красивого вывода
        return json5.dumps(
            formatted_result, indent=2, ensure_ascii=False, quote_keys=True
        )
    except Exception:  # Если json5 не справится со сложными объектами bbox
        return str(formatted_result)  # Простой вывод строки


@register_OCR("google_lens")
class OCRLensAPI(OCRBase):
    # Параметры остаются в основном те же
    params = {
        "delay": 1.0,
        "newline_handling": {
            "type": "selector",
            "options": ["preserve", "remove"],
            "value": "preserve",
            "description": "Handle newline characters in OCR result (only affects final string)",  # Уточнение
        },
        "no_uppercase": {
            "type": "checkbox",
            "value": False,
            "description": "Convert text to lowercase except first letter of sentences",
        },
        "response_method": {
            "type": "selector",
            "options": ["Full Text", "Coordinate sequence", "Location coordinates"],
            "value": "Full Text",
            "description": "Method for extracting/stitching text from image data",  # Уточнение
        },
        "proxy": {
            "value": "",
            "description": 'Proxy address (e.g., http://user:pass@host:port, socks5://host:port, or dict {"http://": ..., "https://": ...})',  # Обновлено описание
        },
        "description": "OCR using Google Lens API (New Engine)",  # Обновлено
    }

    # Свойства остаются те же
    @property
    def request_delay(self):
        try:
            return float(self.get_param_value("delay"))
        except (ValueError, TypeError):
            return 1.0

    @property
    def newline_handling(self):
        return self.get_param_value("newline_handling")

    @property
    def no_uppercase(self):
        return self.get_param_value("no_uppercase")

    @property
    def response_method(self):
        return self.get_param_value("response_method")

    @property
    def proxy(self) -> Optional[Union[str, Dict[str, str]]]:
        val = self.get_param_value("proxy")
        # Пробуем распарсить как JSON-словарь, если строка начинается с {
        if isinstance(val, str) and val.strip().startswith("{"):
            try:
                parsed_dict = json5.loads(val)
                if isinstance(parsed_dict, dict):
                    return parsed_dict
            except Exception:
                pass  # Если не парсится как словарь, оставляем строкой
        return val if val else None  # Возвращаем None если пустая строка

    def __init__(self, **params) -> None:
        # Инициализация базового класса
        super().__init__(**params)
        # Инициализация API с текущим прокси
        self.api = LensAPI(proxy=self.proxy)
        self.last_request_time = 0

    def _ocr_blk_list(
        self, img: np.ndarray, blk_list: List[TextBlock], *args, **kwargs
    ):
        im_h, im_w = img.shape[:2]
        if self.debug_mode:
            self.logger.debug(f"Image size: {im_h}x{im_w}")
        for blk in blk_list:
            x1, y1, x2, y2 = blk.xyxy
            if self.debug_mode:
                self.logger.debug(f"Processing block: ({x1, y1, x2, y2})")
            if 0 <= y1 < y2 <= im_h and 0 <= x1 < x2 <= im_w:
                cropped_img = img[y1:y2, x1:x2]
                if cropped_img.size > 0:  # Доп. проверка, что кроп не пустой
                    if self.debug_mode:
                        self.logger.debug(f"Cropped image size: {cropped_img.shape}")
                    blk.text = self.ocr(cropped_img)  # Вызываем основной метод OCR
                else:
                    if self.debug_mode:
                        self.logger.warning(
                            f"Empty cropped image for block: ({x1, y1, x2, y2})"
                        )
                    blk.text = ""
            else:
                if self.debug_mode:
                    self.logger.warning(
                        f"Invalid text bbox {blk.xyxy} for image size {im_h}x{im_w}"
                    )
                blk.text = ""

    def ocr_img(self, img: np.ndarray) -> str:
        if self.debug_mode:
            self.logger.debug(f"ocr_img shape: {img.shape}")
        return self.ocr(img)

    def ocr(self, img: np.ndarray) -> str:
        if self.debug_mode:
            self.logger.debug(f"Starting OCR on image shape: {img.shape}")
        self._respect_delay()
        try:
            if img.size == 0:
                if self.debug_mode:
                    self.logger.warning("Empty image provided for OCR")
                return ""

            is_success, buffer = cv2.imencode(
                ".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            )
            if not is_success:
                if self.debug_mode:
                    self.logger.error("Failed to encode image to JPEG buffer")
                return ""

            # Вызываем API
            result = self.api.process_image(
                image_buffer=buffer.tobytes(), response_method=self.response_method
            )

            if self.debug_mode:
                formatted_res_str = format_ocr_result(result)
                self.logger.debug(f"OCR raw result:\n{formatted_res_str}")

            full_text = result.get("full_text", "")

            if self.newline_handling == "remove":
                full_text = full_text.replace("\n", " ").replace(
                    "\r", ""
                )  # Убираем и \r

            full_text = self._apply_punctuation_and_spacing(full_text)

            if self.no_uppercase:
                full_text = self._apply_no_uppercase(full_text)

            return str(full_text) if full_text is not None else ""

        except Exception as e:
            if self.debug_mode:
                self.logger.error(f"OCR error occurred", exc_info=True)
            else:
                self.logger.error(f"OCR error: {type(e).__name__} - {e}")
            return ""

    def _apply_no_uppercase(self, text: str) -> str:
        def process_sentence(sentence):
            sentence = sentence.strip()
            if not sentence:
                return ""
            return sentence[0].upper() + sentence[1:].lower()

        sentences = re.split(r"(?<=[.!?…])\s+", text)
        processed_sentences = [process_sentence(s) for s in sentences if s]

        return " ".join(processed_sentences)

    def _apply_punctuation_and_spacing(self, text: str) -> str:
        text = re.sub(r"\s+([,.!?…:;])", r"\1", text)
        text = re.sub(r"([,.!?…:;])(?![,.!?…:;\s])(?!\Z)", r"\1 ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _respect_delay(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        delay = self.request_delay

        if time_since_last_request < delay:
            sleep_time = delay - time_since_last_request
            if self.debug_mode:
                self.logger.info(
                    f"Delay active. Sleeping for {sleep_time:.3f} seconds (Delay: {delay:.1f}s, Since last: {time_since_last_request:.3f}s)"
                )
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def updateParam(self, param_key: str, param_content: Any):
        if param_key == "delay":
            try:
                param_content = float(param_content)
            except (ValueError, TypeError):
                param_content = 1.0

        super().updateParam(param_key, param_content)

        if param_key == "proxy":
            if self.debug_mode:
                self.logger.info(
                    f"Proxy parameter updated to: {self.proxy}. Reinitializing LensAPI."
                )
            try:
                self.api = LensAPI(proxy=self.proxy)
            except Exception as e:
                self.logger.error(
                    f"Failed to reinitialize LensAPI after proxy update: {e}",
                    exc_info=True,
                )
