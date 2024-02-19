import re

from Pars import Pars


class Parsing52(Pars):
    PGN = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
    PGN_PATTERN = r'5\.3\.[\d,\?]+'

    def __init__(self, file_path: str, pattern: str, flag_stop_pattern):
        super().__init__(file_path, pattern, flag_stop_pattern)
        self.__parsed_data = {}

    @property
    def parsed_data(self):
        return self.__parsed_data

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

        while not (re.findall(self._head_pattern, pars_str) or self._stop_check(pars_str, self._flag_stop_pattern)):
            check_png = re.split(self.PGN_PATTERN, pars_str.strip(self.PGN))[:-1]

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
            self.__parsed_data.setdefault(key, paragraph_dict)

            if extra_name:
                self.__parsed_data.setdefault(key + " " + extra_name, paragraph_dict)
        return pars_str
