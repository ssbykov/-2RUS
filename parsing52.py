import re

from PyPDF2 import PdfReader


class Parsing52:
    PGN = "PGN Parameter Group Name and Acronym  Doc. and Paragraph"
    PGN_PATTERN = r'5\.3\.[\d,\?]+'
    BOTTOM_PAGE = "J1939 –71 Database Report April 15, 2001"

    def __init__(self, file_path: str, pattern: str):
        self.__str_list = None
        self.paragraphs = {}
        self.__pages = iter(PdfReader(file_path).pages)
        self.pattern = pattern
        self.__stop_flag = False
        self.last_page = 0
        self.__key = ""

    def parsing52(self):
        for self.__page in self.__pages:
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            if self.__stop_flag:
                break
            head_str = self.__find_head()
            while head_str:
                next_str = self.__add_paragraph(*head_str)
                head_str = self.__find_head(next_str)

        return self.paragraphs

    def __find_head(self, pars_str=""):
        while True:
            if self.__stop_flag:
                break
            if "-71 5.3." == pars_str.strip()[:8]:
                self.last_page = self.__page.extract_text().strip().split()[1]
                self.__stop_flag = True
            substr_position = pars_str.find(self.pattern)
            if substr_position != -1:
                sub_str = pars_str[substr_position + 3:].strip()
                space_position = sub_str.strip().find(" ")
                name = sub_str.strip()[space_position:].strip()
                doc_paragraph = sub_str[:space_position + 1].strip()
                return doc_paragraph, name
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
                slot_scaling = pars_str[len("Slot Scaling: "):].split(",")[0].strip()
            elif "Slot Range:" in pars_str:
                slot_range = pars_str[len("Slot Range: "):].split("Operational Range:")[0].strip()
            elif "SPN:" in pars_str:
                spn = pars_str[len("SPN: "):].strip()
            pars_str = self.__next_str()

        while True:
            check_png = re.split(self.PGN_PATTERN, pars_str.strip(self.PGN))[:-1]
            # if pars_str.strip() == self.PGN or self.PGN in pars_str.strip() and not check_png:
            if "-71 5.2." == pars_str.strip()[:8]:
                break
            elif "-71 5.3." == pars_str.strip()[:8]:
                self.last_page = self.__page.extract_text().strip().split()[1]
                self.__stop_flag = True
                break
            if check_png:
                pngs.extend([p.split()[0] for p in check_png])

            pars_str = self.__next_str()

        for png in pngs:
            key = f"{doc_paragraph}_{png}_{name}"

            self.paragraphs.setdefault(
                key,
                {
                    "name": name,
                    "Slot Scaling": slot_scaling,
                    "Slot Range": slot_range,
                    "SPN": spn,
                    "PNG": png
                }
            )

            if extra_name:
                self.paragraphs.setdefault(
                    key + " " + extra_name,
                    {
                        "name": name,
                        "Slot Scaling": slot_scaling,
                        "Slot Range": slot_range,
                        "SPN": spn,
                        "PNG": png
                    }
                )
        return pars_str

    def __next_str(self):
        try:
            return next(self.__str_list).strip()
        except StopIteration:
            self.__page = next(self.__pages)
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            next_str = next(self.__str_list)
            if self.BOTTOM_PAGE in next_str:
                next_str = next_str[next_str.find(self.BOTTOM_PAGE) + len(self.BOTTOM_PAGE):].strip()
            return next_str.strip()
