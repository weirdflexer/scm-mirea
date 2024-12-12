import argparse
import re
import toml
import sys


class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.current_dict_stack = []
        self.current_key_stack = []
        self.current_parsed_dict = {}

    def parse(self, input_text):
        lines = input_text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("def "):
                self._define_constant(line)
            elif line == "{":
                self._start_dictionary()
            elif line == "}":
                self._end_dictionary()
            elif re.match(r"[_a-zA-Z0-9]+\s*->\s*{", line):
                self._start_nested_dictionary(line)
            elif self._current_dict() is not None:
                self._add_to_dictionary(line)

        if self._current_dict() is not None:
            raise SyntaxError("Unclosed dictionary detected.")

        return self.current_parsed_dict

    def _current_dict(self):
        return self.current_dict_stack[-1] if self.current_dict_stack else None

    def _define_constant(self, line):
        match = re.match(r"def\s+([_A-Z][_a-zA-Z0-9]*)\s*:=\s*(.+)", line)
        if not match:
            raise SyntaxError(f"Invalid constant definition: {line}")
        name, value = match.groups()
        self.constants[name] = self._evaluate_value(value)

    def _evaluate_value(self, value):
        value = value.strip()
        if value.startswith("@[") and value.endswith("]"):
            constant_name = value[2:-1]
            if constant_name not in self.constants:
                raise ValueError(f"Undefined constant: {constant_name}")
            return self.constants[constant_name]
        try:
            return int(value)
        except ValueError:
            return value

    def _start_dictionary(self):
        new_dict = {}
        if self._current_dict() is not None:
            self.current_dict_stack.append(self._current_dict())
        self.current_dict_stack.append(new_dict)

    def _end_dictionary(self):
        if len(self.current_dict_stack) <= 0:
            raise SyntaxError("No dictionary to close.")

        current_dict = self.current_dict_stack.pop()

        if self.current_key_stack:
            parent_key = self.current_key_stack.pop()
            if self._current_dict() is not None:
                self._current_dict()[parent_key] = current_dict
            else:
                self.current_parsed_dict[parent_key] = current_dict
        else:
            self.current_parsed_dict.update(current_dict)

    def _start_nested_dictionary(self, line):
        match = re.match(r"([_a-zA-Z0-9]+)\s*->\s*{", line)
        if not match:
            raise SyntaxError(f"Invalid syntax: {line}")
        key = match.group(1)
        new_dict = {}
        if self._current_dict() is not None:
            self._current_dict()[key] = new_dict
        self.current_dict_stack.append(new_dict)
        self.current_key_stack.append(key)

    def _add_to_dictionary(self, line):
        match = re.match(r"([_a-zA-Z0-9]+)\s*->\s*(\S+)\.", line)
        if not match:
            raise SyntaxError(f"Invalid dictionary entry: {line}")
        key, value = match.groups()
        if self._current_dict() is not None:
            self._current_dict()[key] = self._evaluate_value(value)


def main():
    parser = argparse.ArgumentParser(description="CLI Config Language Parser")
    parser.add_argument("input_file", help="Path to the input file")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            input_text = f.read()

        parser = ConfigParser()
        parsed_output = parser.parse(input_text)

        # Write the parsed output to standard output
        print(toml.dumps(parsed_output))

    except FileNotFoundError:
        print(f"Error: File not found - {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Value Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
