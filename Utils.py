from progressbar import progressbar
from translatepy.translators.yandex import YandexTranslate


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def translate(data_list: list, field: str, chunk_size=50, sep="..", prefix="Rus"):
    """Функция translate принимает на вход список словарей data_list, поле field, размер chunk_size для разбиения
    данных на части, разделитель sep для соединения частей перед отправкой на перевод и префикс prefix для нового
    поля с переведенными данными. Для перевода используется API Яндекс Переводчика. Данные из списка data_list
    разбиваются на части указанного размера, которые затем собираются в одну строку с разделителем sep. Эта строка
    отправляется на перевод на русский язык. Переведенная строка разбивается обратно на части, которые затем
    добавляются к исходным записям в новом словаре с префиксом "Rus" перед именем поля. Итоговые записи с
    переведенными данными добавляются в список translated_data_list. Функция возвращает список словарей с
    добавленными полями, содержащими переведенные данные."""
    ytranslate = YandexTranslate()
    translated_data_list = []
    pbar_max = len(data_list) / chunk_size
    for data_chunk in progressbar(chunks(data_list, chunk_size), max_value=pbar_max, prefix="Переведено:"):
        data_part = sep.join([record.get(field) for record in data_chunk])
        translated_fields = ytranslate.translate(data_part, "Russian").result.split(sep)
        new_records = [record.copy() | {prefix + field: tr_field}
                       for record, tr_field in zip(data_chunk, translated_fields)]
        translated_data_list.extend(new_records)
    return translated_data_list
