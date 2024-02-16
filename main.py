from pprint import pprint

from parsing52 import Parsing52
from parsing53 import Parsing53

file_name = "SAE J1939-71.pdf"


def keyword_pars(pars_str: str):
    pars_keys = ["Slot Scaling", "Slot Range", "SPN"]
    return any([key in pars_str for key in pars_keys])


if __name__ == "__main__":
    parsing52 = Parsing52(file_name, "-71 5.2")
    parsing52.parsing52()
    pprint(parsing52.paragraphs)

    parsing53 = Parsing53(file_name, "-71 5.3", int("331"))
    try:
        paragraphs = parsing53.parsing53()
    except StopIteration:
        # pprint(parsing53.params_dict)
        for _ in parsing53.params:
            # print(_)
            print(f"{_['paragraph_number']}_{_['PGN']}_{_['Name']}")
            print(parsing52.paragraphs.get(f"{_['paragraph_number']}_{_['PGN']}_{_['Name']}", "НЕТ"))
        print(len(parsing53.params))
    #
    # pprint(paragraphs)
    # print(len(paragraphs))
    # print(parsing52.last_page)
