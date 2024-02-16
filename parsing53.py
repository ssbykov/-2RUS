import re

from PyPDF2 import PdfReader


class Parsing53:
    START_HEAD_FLAG = "-71"
    PATTERN52 = (r'([\d|\.|]+|[a-z])\s([\d,\s,a-z]+|Variabl)\s+(.+)\s+(\d+)\s+-71\s+([\d|\.|\?]+)(\s+\d+\/\d+\/\d+)?')
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"

    def __init__(self, file_path: str, pattern: str, page_number: int):
        self.__str_list = None
        self.params = []
        self.params_dict = {}
        self.__pages = iter(PdfReader(file_path).pages[page_number:])
        self.pattern = pattern

    def parsing53(self):
        for self.__page in self.__pages:
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            head_str = self.__find_head()
            while head_str:
                next_str = self.__add_paragraph(*head_str)
                head_str = self.__find_head(next_str)

    def __find_head(self, next_str=""):

        while True:
            str_list = [el.strip() for el in next_str.split(" ")]
            pos_71_lst = [i for i, el in enumerate(reversed(str_list)) if el == self.START_HEAD_FLAG]
            if pos_71_lst and "5.3." in next_str and str_list[-2] == "-":
                pos_71 = pos_71_lst[-1]
                if pos_71 and str_list[-2] == "-":
                    name = " ".join(str_list[-pos_71 + 1:-3]).strip()
                    doc_paragraph = str_list[-pos_71]
                    return doc_paragraph, name
            next_str = self.__next_sub_str_paragraph().strip()

    def __add_paragraph(self, doc_paragraph: str, name: str):
        buffer_str_name = ""
        self.params_dict[doc_paragraph] = []
        pars_str = self.__next_sub_str_paragraph()
        data_length = pgn = paragraph_id = ""
        while "POS Length  Parameter Name  SPN and paragraph  Approved" not in pars_str:
            if "Data Length:" in pars_str:
                data_length = pars_str[len("Data Length: "):].split(",")[0].strip()
            elif "Parameter Group" in pars_str:
                pgn_id = re.findall(r'Parameter Group\s+(\d+)\s+\(\s+(\w+)\s+\)', pars_str)[0]
                pgn = pgn_id[0]
                paragraph_id = pgn_id[1]
            pars_str = self.__next_sub_str_paragraph()

        pars_str = self.__next_sub_str_paragraph()
        while pars_str[:3] != self.START_HEAD_FLAG:
            check_52 = re.findall(self.PATTERN52, pars_str)
            if check_52:
                if buffer_str_name:
                    self.params[-1]["Name"] += buffer_str_name
                    buffer_str_name = ""
                if self.params:
                    self.params_dict[doc_paragraph].append(self.params[-1])
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
            pars_str = self.__next_sub_str_paragraph()
        self.params_dict[doc_paragraph].append(self.params[-1])
        self.params_dict[doc_paragraph].pop(0)
        if buffer_str_name:
            self.params[-1]["Name"] += buffer_str_name
        return pars_str

    def __next_sub_str_paragraph(self):
        try:
            return next(self.__str_list).strip()
        except StopIteration:
            self.__page = next(self.__pages)
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            next_str = next(self.__str_list).strip()
            if self.BOTTOM_PAGE in next_str:
                next_str = next_str[next_str.find(self.BOTTOM_PAGE) + len(self.BOTTOM_PAGE):].strip()
            return next_str
