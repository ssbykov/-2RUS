from progressbar import progressbar
from translatepy.translators.yandex import YandexTranslate


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def translate(data_list: list, field: str):
    chunk_size = 50
    ytranslate = YandexTranslate()
    translated_data_list = []
    for data_chunk in progressbar(chunks(data_list, chunk_size), max_value=len(data_list) / chunk_size,
                                  prefix="Переведено:"):
        data_part = "..".join([record.get(field) for record in data_chunk])
        translated_fields = ytranslate.translate(data_part, "Russian").result.split("..")
        new_records = [record.copy() | {"Rus" + field: tr_field}
                       for record, tr_field in zip(data_chunk, translated_fields)]
        translated_data_list.extend(new_records)
    return translated_data_list
