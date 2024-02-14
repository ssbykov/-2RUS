from pprint import pprint

import pdfplumber
from PyPDF2 import PdfReader

from parsing import Parsing

file_name = "SAE J1939-71.pdf"


def keyword_pars(pars_str: str):
    pars_keys = ["Slot Scaling", "Slot Range", "SPN"]
    return any([key in pars_str for key in pars_keys])


if __name__ == "__main__":
    parsing = Parsing(file_name, "-71 5.2")

    paragraphs = parsing.parsing52()
    pprint(paragraphs)
    print(len(paragraphs))
    print(parsing.last_page)
