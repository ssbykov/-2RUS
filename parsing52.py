import re

from progressbar import ProgressBar

from Pars import Pars


class Parsing52(Pars):
    PGN = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
    PGN_PATTERN = r'5\.3\.[\d,\?]+'
    FLAG_STOP_PATTERN = "-71 5.3."

    def __init__(self, file_path: str, pattern: str):
        super().__init__(file_path)
        self.paragraphs = {}
        self.__pattern = pattern

    def pars(self):
        print(f"\nЗапущен процесс сбора данных по маркеру {self.__pattern}")
        # self._pbar = ProgressBar(max_value=len(self.pdf_reader), redirect_stdout=True)
        while not self._stop_flag:
            pars_page = self._next_page()
            self._str_list = iter(pars_page.extract_text().split("\n"))
            head_str = self.__find_head()
            while not self._stop_flag:
                next_str = self.__add_paragraph(*head_str)
                head_str = self.__find_head(next_str)

        return self.paragraphs

    def __find_head(self, pars_str=""):
        while not self._stop_flag:
            self.__stop_check(pars_str)
            substr_position = pars_str.find(self.__pattern)
            if substr_position != -1:
                sub_str = pars_str[substr_position + 3:].strip()
                space_position = sub_str.strip().find(" ")
                name = sub_str.strip()[space_position:].strip()
                doc_paragraph = sub_str[:space_position + 1].strip()
                return doc_paragraph, name
            pars_str = self._next_str()

    def __add_paragraph(self, doc_paragraph: str, name: str):
        pngs = []
        pars_str = self._next_str()
        if len(pars_str.split()) < 4:
            extra_name = pars_str
        else:
            extra_name = ""
        slot_scaling = slot_range = spn = ""
        while self.PGN not in pars_str and not self._stop_flag:
            if "Slot Scaling:" in pars_str:
                slot_scaling = pars_str.strip("Slot Scaling: ").split(",")[0].strip()
            elif "Slot Range:" in pars_str:
                slot_range = pars_str.strip("Slot Range: ").split("Operational Range:")[0].strip()
            elif "SPN:" in pars_str:
                spn = pars_str.strip("SPN: ").strip()
            pars_str = self._next_str()

        while True:
            check_png = re.split(self.PGN_PATTERN, pars_str.strip(self.PGN))[:-1]
            if pars_str.strip()[:8] == self.__pattern or self.__stop_check(pars_str) or self._stop_flag:
                break
            if check_png:
                pngs.extend([p.split()[0] for p in check_png])

            pars_str = self._next_str()

        for pgn in pngs:
            key = f"{doc_paragraph}_{pgn}_{name}"
            paragraph_dict = {
                "Name": name,
                "Slot Scaling": slot_scaling,
                "Slot Range": slot_range,
                "SPN": spn,
                "PGN": pgn,
                "paragraph_number": doc_paragraph
            }
            self.paragraphs.setdefault(key, paragraph_dict)

            if extra_name:
                self.paragraphs.setdefault(key + " " + extra_name, paragraph_dict)
        return pars_str

    def __stop_check(self, pars_str: str):
        if pars_str.strip()[:8] == self.FLAG_STOP_PATTERN:
            self._stop_flag = True
            return True
        return False
