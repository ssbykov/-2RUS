import re

from Pars import Pars


class Parsing52(Pars):

    def __init__(self, file_path: str, pattern: str, flag_stop_pattern):
        super().__init__(file_path, pattern, flag_stop_pattern)
        self.__parsed_data = {}

    @property
    def parsed_data(self):
        return self.__parsed_data

    def _add_paragraph(self, head: dict):
        # маркер начала раздела с данными по параметру PGN
        pgn_marker = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
        # ключевые паттерны для определения строк с искомыми данными
        scaling_pattern = r'Slot Scaling:\s+(.+)\s,.+\sOffset$'
        range_pattern = r'Slot Range:\s+(.+)\s+Operational Range:.+?$'
        spn_pattern = r'SPN:\s(.+)$'
        pgn_pattern = r'\s-71 5.3.[\d,\?]+'
        # инициализация переменных перед запуском цикла распознавания
        name = head["name"]
        doc_number = head["doc_number"]
        pgn_list = []
        pars_str = self._next_str()
        if len(pars_str.split()) < 4:
            extra_name = pars_str
        else:
            extra_name = ""
        slot_scaling = slot_range = spn = ""

        # цикл для извлечения данных Scaling, Range, SPN
        while pgn_marker not in pars_str and not self._stop_flag:
            if "Slot Scaling:" in pars_str:
                slot_scaling = re.findall(scaling_pattern, pars_str)[0].strip()
            elif "Slot Range:" in pars_str:
                slot_range = re.findall(range_pattern, pars_str)[0].strip()
            elif "SPN:" in pars_str:
                spn = re.findall(spn_pattern, pars_str)[0].strip()
            pars_str = self._next_str()

        # цикл для извлечения данных PGN
        while not (re.findall(self._head_pattern, pars_str) or self._stop_check(pars_str, self._flag_stop_pattern)):
            check_pgn = re.split(pgn_pattern, pars_str.strip(pgn_marker))[:-1]

            if check_pgn:
                pgn_list.extend([p.split()[0] for p in check_pgn])

            pars_str = self._next_str()

        # добавление записи в словарь данных
        for pgn in pgn_list:
            key = f"{doc_number}_{pgn}_{name}"
            paragraph_dict = {
                "Name": name,
                "Slot Scaling": slot_scaling,
                "Slot Range": slot_range,
                "SPN": spn,
                "PGN": pgn,
                "paragraph_number": doc_number
            }
            self.__parsed_data.setdefault(key, paragraph_dict)

            if extra_name:
                self.__parsed_data.setdefault(key + " " + extra_name, paragraph_dict)
        return pars_str
