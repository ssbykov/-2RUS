import re

from PyPDF2 import PdfReader
from progressbar import ProgressBar

from Pars import Pars


class Parsing53(Pars):
    START_HEAD_FLAG = "-71"
    PATTERN52 = (r'([\d|\.|]+|[a-z])\s([\d,\s,a-z]+|Variabl)\s+(.+)\s+(\d+)\s+-71\s+([\d|\.|\?]+)(\s+\d+\/\d+\/\d+)?')
    PATTERN_PARAMETER_GROUP = r'Parameter Group\s+(\d+)\s+\(\s+(\w+)\s+\)'

    def __init__(self, file_path: str, pattern: str, page_number: int):
        super().__init__(file_path)
        self.params = []
        self.last_page = page_number - 1
        self._pages = iter(self.pdf_reader[self.last_page:])
        self.pattern = pattern

    def pars(self):
        print("\nЗапущен процесс сбора данных по номеру 5.3.")
        self._pbar.update(self.last_page)
        while not self._stop_flag:
            pars_page = self._next_page()
            self._str_list = iter(pars_page.extract_text().split("\n"))
            self.__find_head()
            while not self._stop_flag:
                next_str = self.__add_paragraph()
                self.__find_head(next_str)

    def check_52(self, dict_52: dict):
        not_recognized_lst = [param for param in self.params
                  if not dict_52.get(f"{param['paragraph_number']}_{param['PGN']}_{param['Name']}")]

        print(f"\nНе распознано {len(not_recognized_lst)} строк")
        for res in not_recognized_lst:
            # print(res)
            variants = [val for val in dict_52.values()
                   if val["PGN"] == res["PGN"] and val["paragraph_number"] == res["paragraph_number"]
                   and (val["Name"] in res["Name"] or res["Name"] in val["Name"])]

            print(variants)

    def __find_head(self, next_str=""):
        while not self._stop_flag:
            str_list = [el.strip() for el in next_str.split(" ")]
            pos_71_lst = [i for i, el in enumerate(reversed(str_list)) if el == self.START_HEAD_FLAG]
            if pos_71_lst and "5.3." in next_str and str_list[-2] == "-":
                pos_71 = pos_71_lst[-1]
                if pos_71 and str_list[-2] == "-":
                    return
            next_str = self._next_str().strip()

    def __add_paragraph(self):
        buffer_str_name = ""
        pars_str = self._next_str()
        data_length = pgn = paragraph_id = ""
        while "POS Length  Parameter Name  SPN and paragraph  Approved" not in pars_str and not self._stop_flag:
            if "Data Length:" in pars_str:
                data_length = pars_str[len("Data Length: "):].split(",")[0].strip()
            elif "Parameter Group" in pars_str:
                pgn_id = re.findall(self.PATTERN_PARAMETER_GROUP, pars_str)[0]
                pgn = pgn_id[0]
                paragraph_id = pgn_id[1]
            pars_str = self._next_str()

        pars_str = self._next_str()
        while pars_str[:3] != self.START_HEAD_FLAG and not self._stop_flag:
            check_52 = re.findall(self.PATTERN52, pars_str)
            if check_52:
                if buffer_str_name:
                    self.params[-1]["Name"] += buffer_str_name
                    buffer_str_name = ""
                length = check_52[0][1]
                parameter_name = check_52[0][2].strip()
                spn = check_52[0][3]
                paragraph_number = check_52[0][4]
                self.params.append(
                    {
                        "ID": paragraph_id,
                        "Data_length": data_length,
                        "Length": length,
                        "Name": parameter_name,
                        "SPN": spn,
                        "PGN": pgn,
                        "paragraph_number": paragraph_number
                    }
                )
            elif "Variabl" in self.params[-1]["Length"]:
                self.params[-1]["Length"] += " " + pars_str
            elif pars_str.strip():
                buffer_str_name += " " + pars_str.strip()
            else:
                break
            pars_str = self._next_str()
        if buffer_str_name:
            self.params[-1]["Name"] += buffer_str_name
        return pars_str
