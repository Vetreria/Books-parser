# Парсер бибилиотеки


Программа парсит данные о книгах в библиотеке https://tululu.org. 


## Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```



## Запустить


Для работы программы запустите:

```
python main.py
```

По умолчанию программа спарсит книги в диапазоне от 1 до 10 ID включительно.
Если нужно задать другой диапазон, то следует указать его в командной строке цифрами, стартой ID(например 20) и конечный ID (например 50) соответственно.

```
python main.py 20 50
```
Если книги с каким-то ID нет, то в консоль будет выведено сообщение "Книга ID не найдена!"
По завершению сбора данных, будет выведен форматированный словарь со всеми найденными данными.

Для скачивания обложек укажите в командной строке ключ -i

```
python main.py -i
```

Для скачивания книжек укажите ключик -t

```
python main.py -i
```

Можно всё сразу

```
python main.py 20 40 -t -i
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](dvmn.org)