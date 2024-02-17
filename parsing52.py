import re

from PyPDF2 import PdfReader
from tqdm import tqdm


class Parsing52:
    PGN = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
    PGN_PATTERN = r'5\.3\.[\d,\?]+'
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"
    FLAG_STOP_PATTERN = "-71 5.3."
    PGN_STOP_PATTERN = "-71 5.2."

    def __init__(self, file_path: str, pattern: str):
        self.pdf_reader = PdfReader(file_path).pages
        self.__pbar = None
        self.__pages = iter(self.pdf_reader)
        self.__str_list = None
        self.paragraphs = {}
        self.pattern = pattern
        self.__stop_flag = False
        self.last_page = 0
        self.__key = ""

    def parsing52(self):
        print(f"Запущен процесс поиска данных по флагу {self.PGN_STOP_PATTERN}")
        self.__pbar = tqdm(total=len(self.pdf_reader))
        while True:
            pars_page = self.__next_page()
            if self.__stop_flag or not pars_page:
                break
            self.__str_list = iter(pars_page.extract_text().split("\n"))
            head_str = self.__find_head()
            while head_str:
                next_str = self.__add_paragraph(*head_str)
                if self.__stop_flag:
                    break
                head_str = self.__find_head(next_str)

        return self.paragraphs

    def __find_head(self, pars_str=""):
        while True:
            self.__stop_check(pars_str)
            substr_position = pars_str.find(self.pattern)
            if substr_position != -1:
                sub_str = pars_str[substr_position + 3:].strip()
                space_position = sub_str.strip().find(" ")
                name = sub_str.strip()[space_position:].strip()
                doc_paragraph = sub_str[:space_position + 1].strip()
                return doc_paragraph, name
            if self.__stop_flag:
                break
            pars_str = self.__next_str()

    def __add_paragraph(self, doc_paragraph: str, name: str):
        pngs = []
        pars_str = self.__next_str()
        if len(pars_str.split()) < 4:
            extra_name = pars_str
        else:
            extra_name = ""
        slot_scaling = slot_range = spn = ""
        while self.PGN not in pars_str:
            if "Slot Scaling:" in pars_str:
                slot_scaling = pars_str.strip("Slot Scaling: ").split(",")[0].strip()
            elif "Slot Range:" in pars_str:
                slot_range = pars_str.strip("Slot Range: ").split("Operational Range:")[0].strip()
            elif "SPN:" in pars_str:
                spn = pars_str.strip("SPN: ").strip()
            if self.__stop_flag:
                break
            pars_str = self.__next_str()

        while True:
            check_png = re.split(self.PGN_PATTERN, pars_str.strip(self.PGN))[:-1]
            if pars_str.strip()[:8] == self.PGN_STOP_PATTERN or self.__stop_check(pars_str) or self.__stop_flag:
                break
            if check_png:
                pngs.extend([p.split()[0] for p in check_png])

            pars_str = self.__next_str()

        for png in pngs:
            key = f"{doc_paragraph}_{png}_{name}"
            paragraph_dict = {
                "name": name,
                "Slot Scaling": slot_scaling,
                "Slot Range": slot_range,
                "SPN": spn,
                "PNG": png
            }
            self.paragraphs.setdefault(key, paragraph_dict)

            if extra_name:
                self.paragraphs.setdefault(key + " " + extra_name, paragraph_dict)
        return pars_str

    def __stop_check(self, pars_str: str):
        if pars_str.strip()[:8] == self.FLAG_STOP_PATTERN:
            self.__stop_flag = True
            return True
        return False

    def __next_str(self):
        try:
            return next(self.__str_list).strip()
        except StopIteration:
            next_page = self.__next_page()
            if next_page:
                self.__str_list = iter(next_page.extract_text().split("\n"))
                next_str = next(self.__str_list)
                if self.BOTTOM_PAGE in next_str:
                    next_str = next_str[next_str.find(self.BOTTOM_PAGE) + len(self.BOTTOM_PAGE):].strip()
                return next_str.strip()
            else:
                return ""

    def __next_page(self):
        if self.last_page < self.__pbar.total:
            self.last_page += 1
            self.__pbar.update()
            return next(self.__pages)
        else:
            self.__stop_flag = True
