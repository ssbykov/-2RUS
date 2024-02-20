import re

from Pars import Pars


class Parsing53(Pars):
    START_HEAD_FLAG = "-71"
    PATTERN52 = (r'([\d|\.|]+|[a-z])\s([\d,\s,a-z]+|Variabl)\s+(.+)\s+(\d+)\s+-71\s+([\d|\.|\?]+)(\s+\d+\/\d+\/\d+)?')
    PATTERN_PARAMETER_GROUP = r'Parameter Group\s+(\d+)\s+\(\s+(\w+)\s+\)'

    def __init__(self, file_path: str, pattern: str, page_number: int):
        super().__init__(file_path, pattern)
        self.__parsed_data = []
        self.last_page = page_number - 1
        self._pages = iter(self.pdf_reader[self.last_page:])

    @property
    def parsed_data(self):
        return self.__parsed_data

  
    def check_52(self, dict_52: dict):
        def key(rec):
            return f"{rec['paragraph_number']}_{rec['PGN']}_{rec['Name']}"

        recognized_lst = []
        for record in self.__parsed_data:
            if dict_52.get(key(record)):
                recognized_lst.append(record)

        recognized_lst = [
            {
                "ID": record["ID"],
                "Data_length": record["Data_length"],
                "Length": record["Length"],
                "Name": record["Name"],
                "RusName": "",
                "Scaling": dict_52.get(key(record))["Slot Scaling"],
                "Range": dict_52.get(key(record))["Slot Range"],
                "SPN": dict_52.get(key(record))["SPN"],
            } for record in self.__parsed_data
            if dict_52.get(key(record))]

        not_recognized_lst = [param for param in self.__parsed_data
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
            print(f"\nПоследние {len(not_recognized_lst) - len(not_recognized_finally)}"
                  f" записей добавлены в базу были сопоставлены путем частичного, максимального совпадения имен.")
            print(f"Не сопоставлено {len(not_recognized_finally)} записей")
            for record in not_recognized_finally:
                print(record)
        self._pbar.write(f"\nРаспознано {len(recognized_lst)} записей")
        return recognized_lst

    def _add_paragraph(self, head: dict):
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
                    self.__parsed_data[-1]["Name"] += buffer_str_name
                    buffer_str_name = ""
                length = check_52[0][1]
                parameter_name = check_52[0][2].strip()
                spn = check_52[0][3]
                paragraph_number = check_52[0][4]
                self.__parsed_data.append(
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
            elif "Variabl" in self.__parsed_data[-1]["Length"]:
                self.__parsed_data[-1]["Length"] += " " + pars_str
            elif pars_str.strip():
                buffer_str_name += " " + pars_str.strip()
            else:
                break
            pars_str = self._next_str()
        if buffer_str_name:
            self.__parsed_data[-1]["Name"] += buffer_str_name
        return pars_str
