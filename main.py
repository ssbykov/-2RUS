import asyncio

from Utils import translate
from models import load_data
from parsing52 import Parsing52
from parsing53 import Parsing53

file_name = "SAE J1939-71.pdf"

if __name__ == "__main__":
    HEAD_PATTERN_52 = r'-71 (5.2.\d.[\d,\?]+)\s(.+)'
    HEAD_PATTERN_53 = r'-71 (5.3.[\d,\?]+)\s(.+) - [A-Z,\d,\/]+$'
    parsing52 = Parsing52(file_name, HEAD_PATTERN_52, flag_stop_pattern=HEAD_PATTERN_53)
    parsing52.pars()

    parsing53 = Parsing53(file_name, HEAD_PATTERN_53, parsing52.last_page)
    paragraphs = parsing53.pars()
    data_list = parsing53.check_52(parsing52.parsed_data)
    translated_data_list = translate(data_list, "Name")
    asyncio.run(load_data(translated_data_list))
