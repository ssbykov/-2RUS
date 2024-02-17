import re

from PyPDF2 import PdfReader
from progressbar import ProgressBar


class Pars:
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"

    def __init__(self, file_path: str):
        self.pdf_reader = PdfReader(file_path).pages
        self._pages = iter(self.pdf_reader)
        self._str_list = None
        self._stop_flag = False
        self.last_page = 0
        self._pbar = ProgressBar(max_value=len(self.pdf_reader), redirect_stdout=True)

    def _next_str(self):
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

    def _next_page(self):
        if self.last_page < self._pbar.max_value and not self._stop_flag:
            self.last_page += 1
            self._pbar.update(self.last_page)
            return next(self._pages)
        else:
            self._stop_flag = True
