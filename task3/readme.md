
# Конвертер конфигурационного языка в TOML

Этот проект предоставляет инструмент командной строки на Python, который преобразует конфигурационный язык в TOML. Этот язык поддерживает различные конструкции, такие как комментарии, массивы, словари, константы и многое другое. Инструмент обнаруживает и обрабатывает синтаксические ошибки, предоставляя пользователю информативные сообщения об ошибках.

## Особенности

- **Константы**: Поддержка объявления и вычисления констант на этапе трансляции.
- **Числовые и строковые переменные**: поддержка парсинга числовых и строковых.
- **Обработка ошибок**: Надежная обработка ошибок при отсутствии атрибутов или неизвестных констант.
- **Тестирование**: Комплексное тестирование с использованием `unittest` для проверки всех конструкций и преобразований.

## Использование

### Установка

Убедитесь, что у вас установлена версия Python 3.7 или выше.

1. Клонируйте этот репозиторий:

    ```bash
    git clone https://github.com/weirdflexer/scm-mirea
    cd scm-mirea/task3
    ```

2. Установите зависимости:

    ```bash
    pip install toml
    ```

### Использование инструмента командной строки

Вы можете использовать конвертер, указав путь к XML файлу:

```bash
python main.py input.config
```

Это команда прочитает файл `input.config` и выведет соответствующую структуру на языке TOML в стандартный вывод.

#### Пример

Для файла следующего вида:

```
def PORT := 5432

server -> {
    database -> mydb.
    user -> admin.
    port -> @[PORT].
    host -> localhost.
    alpha -> {
        database -> mydb.
    }
    beta -> {
        database -> mydb.
    }
}
```

Запуск команды:

```bash
python main.py input.config
```

Вернет результат:

```plaintext
[server]
database = "mydb"
user = "admin"
port = 5432
host = "localhost"

[server.alpha]
database = "mydb"

[server.beta]
database = "mydb"
```

### Обработка ошибок

Если в файле учебного конфигуриционного языка содержатся недопустимые структуры или ссылки на неизвестные константы, инструмент выдаст ошибку и предоставит полезное сообщение для выявления проблемы.

## Тестирование

Этот проект использует `unittest` для тестирования. Чтобы запустить тесты:

1. Запустите тесты:

    ```bash
    pytest -m unittest tests/tests.py
    ```

Вы увидите подобный вывод:

```bash
......
----------------------------------------------------------------------
Ran 6 tests in 0.000s

OK
```

## Примеры конфигураций

Ниже приведены примеры конфигураций учебного языка из разных предметных областей, которые можно использовать с этим инструментом.

### Конфигурация веб-сервера

**Входной учебный язык:**

```
def PORT := 5432

server -> {
    database -> mydb.
    user -> admin.
    port -> @[PORT].
    host -> localhost.
    alpha -> {
        database -> mydb.
    }
    beta -> {
        database -> mydb.
    }
}
```

**Конвертированный вывод TOML:**

```toml
[server]
database = "mydb"
user = "admin"
port = 5432
host = "localhost"

[server.alpha]
database = "mydb"

[server.beta]
database = "mydb"
```
**Входной учебный язык:**

```
def DEBUG := 1
app -> {
    app_name -> MyApp.
    version -> 1.
    debug_mode -> @[DEBUG].
    api_endpoint -> http://localhost/api.
}
```

**Конвертированный вывод TOML:**

```toml
[app]
app_name = "MyApp"
version = 1
debug_mode = 1
api_endpoint = "http://localhost/api"
```
