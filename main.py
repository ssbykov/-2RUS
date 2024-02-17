from pprint import pprint

from parsing52 import Parsing52
from parsing53 import Parsing53

file_name = "SAE J1939-71.pdf"


def keyword_pars(pars_str: str):
    pars_keys = ["Slot Scaling", "Slot Range", "SPN"]
    return any([key in pars_str for key in pars_keys])


if __name__ == "__main__":
    parsing52 = Parsing52(file_name, "-71 5.2.")
    parsing52.pars()
    # pprint(parsing52.paragraphs)

    parsing53 = Parsing53(file_name, "-71 5.3", parsing52.last_page)
    paragraphs = parsing53.pars()
    parsing53.check_52(parsing52.paragraphs)
    # for _ in parsing53.params:
        # print(_)
        # print(f"{_['paragraph_number']}_{_['PGN']}_{_['Name']}")
        # res = parsing52.paragraphs.get(f"{_['paragraph_number']}_{_['PGN']}_{_['Name']}", "НЕТ")
        # if res == "НЕТ":
        #     print(_)
        # print(parsing52.paragraphs.get(f"{_['paragraph_number']}_{_['PGN']}_{_['Name']}", "НЕТ"))
        # print(len(parsing53.params))
