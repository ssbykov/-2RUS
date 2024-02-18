import asyncio
from datetime import datetime
from pprint import pprint

from Utils import translate
from models import load_data
from parsing52 import Parsing52
from parsing53 import Parsing53


file_name = "SAE J1939-71.pdf"

if __name__ == "__main__":
    parsing52 = Parsing52(file_name, "-71 5.2.")
    parsing52.pars()

    parsing53 = Parsing53(file_name, "-71 5.3", parsing52.last_page)
    paragraphs = parsing53.pars()
    data_list = parsing53.check_52(parsing52.paragraphs)
    translated_data_list = translate(data_list, "Name")
    asyncio.run(load_data(translated_data_list))
