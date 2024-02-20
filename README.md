﻿
Программа для парсинга текстового содержимого из PDF документа.  

**Функциональность:**

Программа принимает входной PDF файл в качестве аргумента. Программа извлекает текстовую информацию из PDF документа и сохраняет извлеченный текст в указанном формате в базу данных.

**Технические требования:**

БД - postgresql.

**Запуск программы:**

Для запуска программы необходимо установить все зависимости из файла requirements.txt выполнением в терминале команды “pip install -r requirements.txt”.

В файле .env указать настройки подключения к базе данных. Базу данных можно развернуть в Docker запуском команды “docker-compose up -d”.

Файл для парсинга можно скопировать либо в папку проекта, либо в файле main.py в переменную file\_name передать путь к файлу на компьютере.

