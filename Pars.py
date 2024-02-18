from PyPDF2 import PdfReader
from tqdm import tqdm


class Pars:
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"
    _pbar = tqdm(total=1, ncols=100)

    def __init__(self, file_path: str, pattern: str):
        self.pdf_reader = PdfReader(file_path).pages
        self._pages = iter(self.pdf_reader)
        self._pattern = pattern
        self._str_list = None
        self._stop_flag = False
        self.last_page = 0
        self._pbar.total = len(self.pdf_reader)

    # def pars(self):
    #     self._pbar.desc = f"Обработка по маркеру {self._pattern}"
    #     while not self._stop_flag:
    #         pars_page = self._next_page()
    #         self._str_list = iter(pars_page.extract_text().split("\n"))
    #         head_str = self.__find_head()
    #         while not self._stop_flag:
    #             next_str = self.__add_paragraph()
    #             head_str = self.__find_head(next_str)
    #
    # def __find_head(self, pars_str=""):
    #     pass
    #
    # def __add_paragraph(self):
    #     pass

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
        if self.last_page < self._pbar.total and not self._stop_flag:
            self.last_page += 1
            self._pbar.update()
            return next(self._pages)
        else:
            self._stop_flag = True
