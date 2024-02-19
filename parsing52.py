import re

from Pars import Pars


class Parsing52(Pars):
    HEAD_PATTERN = r'-71 (5.2.\d.[\d,\?]+)\s(.+)'
    PGN = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
    PGN_PATTERN = r'5\.3\.[\d,\?]+'
    FLAG_STOP_PATTERN = "-71 5.3."

    def __init__(self, file_path: str, pattern: str, flag_stop_pattern):
        super().__init__(file_path, pattern, flag_stop_pattern)
        self._parsed_data = {}

    # def _find_head(self, pars_str=""):
    #     while not self._stop_flag:
    #         self.__stop_check(pars_str)
    #         name_number = re.findall(self.HEAD_PATTERN, pars_str)
    #         if name_number:
    #             return {"doc_number": name_number[0][0].strip(), "name": name_number[0][1].strip()}
    #         pars_str = self._next_str()

    def _add_paragraph(self, head: dict):
        name = head["name"]
        doc_number = head["doc_number"]
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
            if pars_str.strip()[:8] == "-71 5.2." or self._stop_check(pars_str, self._flag_stop_pattern) or self._stop_flag:
                break
            if check_png:
                pngs.extend([p.split()[0] for p in check_png])

            pars_str = self._next_str()

        for pgn in pngs:
            key = f"{doc_number}_{pgn}_{name}"
            paragraph_dict = {
                "Name": name,
                "Slot Scaling": slot_scaling,
                "Slot Range": slot_range,
                "SPN": spn,
                "PGN": pgn,
                "paragraph_number": doc_number
            }
            self._parsed_data.setdefault(key, paragraph_dict)

            if extra_name:
                self._parsed_data.setdefault(key + " " + extra_name, paragraph_dict)
        return pars_str

    # def __stop_check(self, pars_str: str):
    #     if pars_str.strip()[:8] == self.FLAG_STOP_PATTERN:
    #         self._stop_flag = True
    #         return True
    #     return False
