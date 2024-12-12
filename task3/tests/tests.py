import unittest
from io import StringIO
from main import ConfigParser


class TestConfigParser(unittest.TestCase):
    def test_parse_basic(self):
        """Тест базового парсинга конфигурации"""
        input_text = """
            database -> {
                user -> admin.
                password -> secret.
            }
        """
        parser = ConfigParser()
        result = parser.parse(input_text)
        expected_output = {
            "database": {
                "user": "admin",
                "password": "secret"
            }
        }
        self.assertEqual(result, expected_output)

    def test_constant_parsing(self):
        """Тест парсинга констант"""
        input_text = """
        def NUM := 23
        {
            value -> @[NUM].
        }
        """
        parser = ConfigParser()
        result = parser.parse(input_text)
        expected_output = {
            "value": 23
        }
        self.assertEqual(result, expected_output)

    def test_nested_dictionaries(self):
        """Тест обработки вложенных словарей"""
        input_text = """
            a -> {
                b -> {
                    c -> value.
                }
            }
        """
        parser = ConfigParser()
        result = parser.parse(input_text)
        expected_output = {
            "a": {
                "b": {
                    "c": "value"
                }
            }
        }
        self.assertEqual(result, expected_output)

    def test_syntax_error(self):
        """Тест на синтаксические ошибки"""
        input_text = """
        def INVALID_CONSTANT :=
        """
        parser = ConfigParser()
        with self.assertRaises(SyntaxError):
            parser.parse(input_text)

    def test_unclosed_braces(self):
        """Тест на незакрытые скобки"""
        input_text = """
        test -> {
            server -> 8080.
        """
        parser = ConfigParser()
        with self.assertRaises(SyntaxError):
            parser.parse(input_text)

    def test_value_error_for_unknown_constant(self):
        """Тест на некорректное использование неизвестной константы"""
        input_text = """
        def PI := 3.14
        test -> {
            value -> @[UNKNOWN].
        }
        """
        parser = ConfigParser()
        with self.assertRaises(ValueError):
            parser.parse(input_text)

if __name__ == "__main__":
    unittest.main()
