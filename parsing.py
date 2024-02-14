from PyPDF2 import PdfReader


class Parsing:
    def __init__(self, file_path: str, pattern: str):
        self.__str_list = None
        self.paragraphs = []
        self.__pages = iter(PdfReader(file_path).pages)
        self.pattern = pattern
        self.__stop_flag = False
        self.last_page = 0

    def parsing52(self):
        for self.__page in self.__pages:
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            if self.__stop_flag:
                break
            self.__pars_page()
        return self.paragraphs

    def __pars_page(self):
        for txt in self.__str_list:
            if "-71 5.3." == txt.strip()[:8]:
                self.last_page = self.__page.extract_text().strip().split()[1]
                self.__stop_flag = True
            substr_position = txt.find(self.pattern)
            if substr_position != -1:
                sub_str = txt[substr_position + 3:]
                space_position = sub_str.strip().find(" ")
                name = sub_str.strip()[space_position:].strip()
                if len(name.split("/")) != 3 and space_position != -1:
                    doc_paragraph = sub_str[:space_position + 1].strip()
                    self.__add_paragraph(doc_paragraph, name)

    def __add_paragraph(self, doc_paragraph: str, name: str):
        sub_str_paragraph = self.__next_sub_str_paragraph()
        slot_scaling = slot_range = spn = ""
        while "Parameter Group Name and Acronym" not in sub_str_paragraph:
            if "Slot Scaling:" in sub_str_paragraph:
                slot_scaling = sub_str_paragraph[len("Slot Scaling: "):].split(",")[0].strip()
            elif "Slot Range:" in sub_str_paragraph:
                slot_range = sub_str_paragraph[len("Slot Range: "):].split("Operational Range:")[0].strip()
            elif "SPN:" in sub_str_paragraph:
                spn = sub_str_paragraph[len("SPN: "):].strip()

            sub_str_paragraph = self.__next_sub_str_paragraph()

        self.paragraphs.append(
            {
                "paragraph_number": doc_paragraph,
                "name": name,
                "slot_scaling": slot_scaling,
                "slot_range": slot_range,
                "spn": spn
            }
        )

    def __next_sub_str_paragraph(self):
        try:
            return next(self.__str_list)
        except StopIteration:
            self.__page = next(self.__pages)
            self.__str_list = iter(self.__page.extract_text().split("\n"))
            return next(self.__str_list)
