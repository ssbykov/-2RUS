import re

from Pars import Pars


class Parsing53(Pars):

    def __init__(self, file_path: str, pattern: str, page_number: int):
        super().__init__(file_path, pattern)
        self.__parsed_data = []
        self.last_page = page_number - 1
        self._pages = iter(self.pdf_reader[self.last_page:])

    @property
    def parsed_data(self):
        return self.__parsed_data

    # метод соединения данных двух разделов
    def check_52(self, dict_52: dict):
        def key(rec):
            return f"{rec['paragraph_number']}_{rec['PGN']}_{rec['Name']}"

        # заполнение списка по совпадающим данным из разделов
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

        # формирование списка по не сопоставленным данным
        not_recognized_lst = [param for param in self.__parsed_data
                              if not dict_52.get(key(param))]

        # сопоставляем нераспознанные записи
        not_recognized_finally, recognized_lst_part = self.__check_52_part(dict_52, not_recognized_lst)
        recognized_lst.extend(recognized_lst_part)

        print(f"Не сопоставлено {len(not_recognized_finally)} записей")
        for record in not_recognized_finally:
            print(record)

        self._pbar.write(f"\nРаспознано {len(recognized_lst)} записей")
        return recognized_lst

    # метод сопоставление данных по полям PGN, номер параграфа и частичное совпадение названий
    @staticmethod
    def __check_52_part(dict_52: dict, not_recognized_lst: list):
        if not_recognized_lst:
            not_recognized_finally = []
            recognized_lst_part = []
            for record in not_recognized_lst:

                # отбор вариантов для сопоставления
                variants = [(min(len(record["Name"]), len(val["Name"])), val) for val in dict_52.values()
                            if val["PGN"] == record["PGN"] and val["paragraph_number"] == record["paragraph_number"]
                            and (val["Name"] in record["Name"] or record["Name"] in val["Name"])]

                # если вариантов для сопоставления нет запись считается не распознанной
                if not variants:
                    not_recognized_finally.append(record)
                    continue

                # из возможных вариантов для сопоставления выбирается наилучший
                mach_variant = max(variants)[1]

                # добавление записи после дополнительной проверки
                recognized_lst_part.append(
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
            return not_recognized_finally, recognized_lst_part

    def _add_paragraph(self, head: dict):
        # маркер начала строки со следующим параграфом 5.3
        start_head_flag = "-71"
        # маркер начала таблицы с данными по параграфам 5.2
        table_marker = "POS Length  Parameter Name  SPN and paragraph  Approved"
        # паттерн извлечения данных по параграфам 5.2
        pattern52 = (
            r'([\d|\.|]+|[a-z])\s([\d,\s,a-z]+|Variabl)\s+(.+)\s+(\d+)\s+-71\s+([\d|\.|\?]+)(\s+\d+\/\d+\/\d+)?')
        # паттерн извлечения данные по ID и PGN
        parameter_group_pattern = r'Parameter Group\s+(\d+)\s+\(\s+(\w+)\s+\)'
        # инициализация переменных перед запуском цикла распознавания
        buffer_str_name = ""
        pars_str = self._next_str()
        data_length = pgn = paragraph_id = ""
        # цикл для извлечения данных для полей Length, PGN, ID
        while table_marker not in pars_str and not self._stop_flag:
            if "Data Length:" in pars_str:
                data_length = pars_str[len("Data Length: "):].split(",")[0].strip()
            elif "Parameter Group" in pars_str:
                pgn_id = re.findall(parameter_group_pattern, pars_str)[0]
                pgn = pgn_id[0]
                paragraph_id = pgn_id[1]
            pars_str = self._next_str()

        pars_str = self._next_str()
        # цикл для извлечения данных NAME, SPG, номер параграфа раздела 5.2
        while pars_str[:len(start_head_flag)] != start_head_flag and not self._stop_flag:
            check_52 = re.findall(pattern52, pars_str)
            if check_52:
                # добавление дополнительной строки для поля NAME
                if buffer_str_name:
                    self.__parsed_data[-1]["Name"] += buffer_str_name
                    buffer_str_name = ""

                # заполнение переменных с данными по разделу 5.2
                length = check_52[0][1]
                parameter_name = check_52[0][2].strip()
                spn = check_52[0][3]

                # добавление записи в список словарей
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
            # проверка на наличие дополнительных строк для поля Length
            elif "Variabl" in self.__parsed_data[-1]["Length"]:
                self.__parsed_data[-1]["Length"] += " " + pars_str
            # проверка на наличие дополнительной строки для поля NAME
            elif pars_str.strip():
                buffer_str_name += " " + pars_str.strip()
            else:
                break
            pars_str = self._next_str()
        # добавление дополнительной строки для поля NAME на выходе из метода
        if buffer_str_name:
            self.__parsed_data[-1]["Name"] += buffer_str_name
        return pars_str
