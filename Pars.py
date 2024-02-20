import re

from PyPDF2 import PdfReader
from tqdm import tqdm
from abc import ABC, abstractmethod


# базовый класс для наследования классов для парсинга отдельных разделов файла
class Pars(ABC):
    # текст содержащийся в последней строке каждой страницы файла
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"
    # переменная для инициализации прогресс-бара
    _pbar = tqdm(total=1, ncols=100, desc="Парсинг страниц")

    def __init__(self, file_path: str, head_pattern: str, flag_stop_pattern=""):
        self.pdf_reader = PdfReader(file_path).pages
        self._pages = iter(self.pdf_reader)
        self._flag_stop_pattern = flag_stop_pattern
        self._head_pattern = head_pattern
        self._str_list = None
        self._stop_flag = False
        self.last_page = 0
        self._pbar.total = len(self.pdf_reader)

    # основной метод для запуска парсинга страниц PDF файла
    def pars(self):
        while not self._stop_flag:
            pars_page = self._next_page()
            self._str_list = iter(pars_page.extract_text().split("\n"))
            head = self._find_head()
            while not self._stop_flag:
                next_str = self._add_paragraph(head)
                head = self._find_head(next_str)

    #  метод для поиска заголовков по указанному шаблону
    def _find_head(self, pars_str="", stop_flag_pattern=""):
        while not self._stop_flag:
            if stop_flag_pattern:
                self._stop_check(pars_str, stop_flag_pattern)
            name_number = re.findall(self._head_pattern, pars_str)
            if name_number:
                return {"doc_number": name_number[0][0].strip(), "name": name_number[0][1].strip()}
            pars_str = self._next_str()

    # абстрактный метод для парсинга данных между заголовками в тексте
    @abstractmethod
    def _add_paragraph(self, kwargs):
        pass

    # метод для получения следующей строки текста
    def _next_str(self) -> str:
        try:
            return next(self._str_list).strip()
        except StopIteration:
            next_page = self._next_page()
            if next_page:
                self._str_list = iter(next_page.extract_text().split("\n"))
                next_str = next(self._str_list)
                if self.BOTTOM_PAGE in next_str:
                    next_str = next_str[next_str.find(self.BOTTOM_PAGE) + len(self.BOTTOM_PAGE):].strip()
                return next_str.strip()
            else:
                return ""

    # метод для перехода к следующей странице PDF файла
    def _next_page(self):
        if self.last_page < self._pbar.total and not self._stop_flag:
            self.last_page += 1
            self._pbar.update()
            return next(self._pages)
        else:
            self._stop_flag = True

    # метод для проверки условия остановки парсинга
    def _stop_check(self, pars_str: str, stop_flag_pattern: str):
        if re.findall(stop_flag_pattern, pars_str):
            self._stop_flag = True
            return True
        return False
