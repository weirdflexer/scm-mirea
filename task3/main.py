import sys
import re
import json

# Словарь для хранения объявленных констант
constants = {}

# Функция для обработки значений
def parse_value(value):
    # Если значение является числом
    if re.match(r'^\d+$', value):
        return int(value)
    # Если значение является вложенным словарем
    elif value.startswith("{") and value.endswith("}"):
        return parse_dict(value)
    # Если значение является константой
    elif value.startswith("@["):
        const_name = value[2:-1]
        return constants.get(const_name, f"ERROR: Unknown constant {const_name}")
    return value

# Функция для обработки словаря
def parse_dict(text):
    # Убираем внешние скобки и разбиваем на строки
    inner_text = text[1:-1].strip()
    result = {}
    lines = inner_text.split("\n")
    for line in lines:
        if '->' in line:
            key, value = line.split('->')
            key = key.strip()
            value = value.strip().rstrip(".")
            result[key] = parse_value(value)
    return result

# Функция для обработки объявления константы
def handle_constant_declaration(line):
    match = re.match(r"def (\w+) := (.+)", line)
    if match:
        const_name = match[1]
        value = match[2].strip()
        constants[const_name] = parse_value(value)

# Основная функция для обработки входного файла
def parse_file(file_path):
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("def"):
                handle_constant_declaration(line)
            elif "->" in line:
                key, value = line.split("->")
                key = key.strip()
                value = value.strip().rstrip(".")
                print(f"{key} = {json.dumps(parse_value(value))}")
            else:
                print(f"ERROR: Invalid syntax in line: {line}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <path_to_input_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    parse_file(file_path)
