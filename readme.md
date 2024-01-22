Скрипт для выкачивания прочитанных книг с сайта LiveLib.
Результат сохраняется в csv формате, открывать в Excel или аналогах.
Есть три варианта работы скрипта. Они отичаются скоростью и набором полученной информации.

Требования:
* Python
* Установить библиотеки из requirements.txt с помощью pip (pip install -r requirements.txt)
  Лучше в отдельную venv

1. Скачать книги из обычного списка прочитанного.
> python script.py username
где username - логин пользователя LiveLib'а
Плюсы:
* не нужна регистрация
* рейтиннг в формате цифры
Минусы:
* много запрсов, долго отрабатывает (приходится ждать между запросами, чтобы сайт не посчитал за спам)
* нет даты прочтения

2. Скачть книги из списка прочитанного, подготовленного для печати.
Вариант 1: скачать список скриптом
> python script2.py online username password
где username - логин пользователя LiveLib'а, password - пароль пользователя LiveLib'а
Плюсы:
* отрабатывает относительно быстро
* можно получить дату прочтения (месяц и год или только год)
Минусы:
* нужна регистрация
* нет серии, в которую входит книга
Вариант 2: скачать список руками и отдать скрипту для формирования csv
> python script2.py from_file path_to_file.html
где path_to_file.html - путь до предварительно скачанного файла.
Чтобы скачать файл:
На странице с прочитанным нажать иконку принтера ("Версия для печати") и сохранить страницу.
Плюсы:
* не нужна регистрация и обращение к интернету
* отрабатывает быстро
* можно получить дату прочтения (месяц и год или только год)
Минусы:
* придется скачать html файл руками
* нет серии, в которую входит книга

3. Как-нибудь имитировать пользователя с использованием Selenium
Пока не реализовано.

Известные баги:
* для книги иногда не парсится автор, потому что LiveLib не выводит его в общем списке, а запрашивать для каждой книги слишком накладно. Чаще всего автор не отображается, если книгу написал коллектив авторов, но иногда так происходит и с одиночными авторами.