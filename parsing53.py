import re

from Pars import Pars


class Parsing53(Pars):
    START_HEAD_FLAG = "-71"
    PATTERN52 = (r'([\d|\.|]+|[a-z])\s([\d,\s,a-z]+|Variabl)\s+(.+)\s+(\d+)\s+-71\s+([\d|\.|\?]+)(\s+\d+\/\d+\/\d+)?')
    PATTERN_PARAMETER_GROUP = r'Parameter Group\s+(\d+)\s+\(\s+(\w+)\s+\)'

    def __init__(self, file_path: str, pattern: str, page_number: int):
        super().__init__(file_path, pattern)
        self.params = []
        self.last_page = page_number - 1
        self._pages = iter(self.pdf_reader[self.last_page:])

    def pars(self):
        self._pbar.desc = f"Обработка по маркеру {self._pattern}"
        while not self._stop_flag:
            pars_page = self._next_page()
            self._str_list = iter(pars_page.extract_text().split("\n"))
            self.__find_head()
            while not self._stop_flag:
                next_str = self.__add_paragraph()
                self.__find_head(next_str)

    def check_52(self, dict_52: dict):
        def key(par):
            return f"{par['paragraph_number']}_{par['PGN']}_{par['Name']}"

        recognized_lst = [
            {
                "ID": param["ID"],
                "Data_length": param["Data_length"],
                "Length": param["Length"],
                "Name": param["Name"],
                "RusName": "",
                "Scaling": dict_52.get(key(param))["Slot Scaling"],
                "Range": dict_52.get(key(param))["Slot Range"],
                "SPN": dict_52.get(key(param))["SPN"],
            } for param in self.params
            if dict_52.get(key(param))]

        not_recognized_lst = [param for param in self.params
                              if not dict_52.get(key(param))]
        if not_recognized_lst:

            not_recognized_finally = []
            for record in not_recognized_lst:
                variants = [(min(len(record["Name"]), len(val["Name"])), val) for val in dict_52.values()
                            if val["PGN"] == record["PGN"] and val["paragraph_number"] == record["paragraph_number"]
                            and (val["Name"] in record["Name"] or record["Name"] in val["Name"])]
                if not variants:
                    not_recognized_finally.append(record)
                    continue
                mach_variant = max(variants)[1]

                # print("Сопоставить запись:")
                # print(record["Name"])
                # print("с записью")
                # print(mach_variant["Name"])
                ans = "1"
                # while ans not in ("0", "1"):
                #     ans = input("Нажмите \"1 - Да или 0 - нет\"\n")
                if ans == "1":
                    recognized_lst.append(
                        {
                            "ID": record["ID"],
                            "Data_length": record["Data_length"],
                            "Length": record["Length"],
                            "Name": record["Name"] if len(record["Name"]) > len(mach_variant["Name"])
                            else mach_variant["Name"],
                            "RusName": "",
                            "Scaling": mach_variant["Slot Scaling"],
                            "Range": mach_variant["Slot Range"],
                            "SPN": mach_variant["SPN"],
                        }
                    )
                else:
                    not_recognized_finally.append(record)
            print(f"\nНе сопоставлено {len(not_recognized_finally)} записей")
            for record in not_recognized_finally:
                print(record)
        self._pbar.write(f"\nРаспознано {len(recognized_lst)} записей")
        return recognized_lst

    def __find_head(self, pars_str=""):
        while not self._stop_flag:
            str_list = [el.strip() for el in pars_str.split(" ")]
            pos_71_lst = [i for i, el in enumerate(reversed(str_list)) if el == self.START_HEAD_FLAG]
            if pos_71_lst and "5.3." in pars_str and str_list[-2] == "-":
                pos_71 = pos_71_lst[-1]
                if pos_71 and str_list[-2] == "-":
                    return
            pars_str = self._next_str().strip()

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
