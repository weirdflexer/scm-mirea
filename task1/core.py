import os
import time
import zipfile
import tkinter as tk
from tkinter import scrolledtext
import configparser
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CSVFormatter(logging.Formatter):
    def __init__(self):
        super().__init__("%(asctime)s,%(name)s,%(levelname)s,%(message)s")
    def format(self, record):
        return super().format(record)


file_handler = logging.FileHandler("app.csv")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(CSVFormatter())
logger.addHandler(file_handler)

class Emulator:
    """
    Класс для эмуляции файловой системы и выполнения команд, аналогичных shell-командам.
    """

    def __init__(self, config_path):
        """
        Инициализация эмулятора, чтение конфигурации.
        """
        self.config = self.read_config(config_path)
        self.vfs_path = self.config['vfs_path']
        self.log_path = self.config['log_path']
        self.startup_script = self.config['startup_script']
        self.current_dir = ''
        self.init_vfs()
        logger.debug('Emulator initialized')

    def read_config(self, config_path):
        """
        Читает конфигурационный файл `.ini` и возвращает параметры.
        """
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            vfs_path = config.get('Paths', 'vfs_path')
            log_path = config.get('Paths', 'log_path')
            startup_script = config.get('Paths', 'startup_script')
            logger.debug('Config loaded: vfs_path=%s, startup_script=%s', vfs_path, startup_script)
            return {'vfs_path': vfs_path, 'log_path': log_path,'startup_script': startup_script}
        except Exception as e:
            logger.error('Error reading config file: %s', e)
            raise

    def init_vfs(self):
        """
        Инициализирует виртуальную файловую систему: открывает ZIP-файл.
        """
        self.zip_ref = zipfile.ZipFile(self.vfs_path, 'r')
        logger.debug('VFS initialized: vfs_path=%s', self.vfs_path)

    def run_startup_script(self):
        """
        Выполняет команды из стартового скрипта.
        """
        script_path = os.path.join(self.current_dir, self.startup_script)
        if script_path in self.zip_ref.namelist():
            with self.zip_ref.open(script_path) as script_file:
                commands = script_file.readlines()
                for command in commands:
                    self.run_command(command.strip().decode('utf-8'))

    def cleanup(self):
        """
        Очищает временные ресурсы.
        """
        logger.debug('Cleaning up...')
        self.zip_ref.close()

    def run_command(self, command, output_widget=None):
        """
        Выполняет указанную команду и выводит результат.
        """
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if output_widget:
            output_widget.insert(tk.END, f"{self.whoami()}$ {command}\n")

        if cmd == 'ls':
            result = self.ls()
        elif cmd == 'cd':
            result = self.cd(args[0]) if args else "cd: missing path"
        elif cmd == 'exit':
            result = self.exit()
        elif cmd == "uname":
            result = self.uname()
        elif cmd == "tail":
            result = self.tail(args[0]) if args else "tail: missing path"
        else:
            result = f"{cmd}: command not found"

        if output_widget:
            output_widget.insert(tk.END, result + "\n")
            output_widget.see(tk.END)

        logger.debug('Command executed: %s', command)
        return result

    def ls(self):
        """
        Выполняет команду 'ls': список файлов и директорий.
        """
        logger.debug('Listing files in current directory: %s', self.current_dir)
        files = [f for f in self.zip_ref.namelist() if f.startswith(self.current_dir)]
        current_dir_files = set()

        for f in files:
            relative_path = f.replace(self.current_dir, '', 1).lstrip('/')
            if '/' not in relative_path:
                current_dir_files.add(relative_path)
            else:
                dir_name = relative_path.split('/')[0]
                current_dir_files.add(dir_name)

        return "\n".join(sorted(current_dir_files))

    def cd(self, path):
        """
        Выполняет команду 'cd'.
        """
        logger.debug('Changing directory: %s', path)
        if path == '..':
            self.current_dir = os.path.normpath(os.path.join(self.current_dir, '..')) + '/'
        else:
            new_path = os.path.join(self.current_dir, path)
            if not new_path.endswith('/'):
                new_path += '/'
            if any(name.startswith(new_path) for name in self.zip_ref.namelist()):
                self.current_dir = new_path
            else:
                return f"cd: {path}: No such file or directory"
        return f"Changed directory to {self.current_dir}"

    def exit(self):
        """
        Выполняет команду 'exit'.
        """
        logger.debug('Exiting emulator...')
        self.cleanup()
        exit()

    def whoami(self):
        """
        Возвращает текущего пользователя.
        """
        return os.getlogin()

    def uname(self):
        """
        Возвращает информацию об эмуляторе.
        """
        return "UnixEmulator"

    def tail(self, path):
        """
        Выполняет команду 'tail'.
        """
        logger.debug('Executing tail command on file: %s', path)
        try:
            file_path = os.path.join(self.current_dir, path)
            if file_path not in self.zip_ref.namelist():
                return f"tail: {path}: No such file"

            with self.zip_ref.open(file_path) as file:
                lines = file.readlines()

            if not lines:
                return "tail: File is empty"

            last_lines = lines[-10:]
            return ''.join(line.decode('utf-8') for line in last_lines)

        except Exception as e:
            logger.error('Error in tail command: %s', e)
            return f"tail: Error: {str(e)}"

class ShellGUI:
    """
    Класс GUI оболочки.
    """
    def __init__(self, emulator):
        self.emulator = emulator
        self.root = tk.Tk()
        self.root.title("Shell Emulator")
        self.output = scrolledtext.ScrolledText(self.root, height=20, width=80, state=tk.NORMAL)
        self.output.pack()
        self.entry = tk.Entry(self.root, width=80)
        self.entry.pack()
        self.entry.bind('<Return>', self.execute_command)
        self.emulator.run_startup_script()

    def execute_command(self, event):
        command = self.entry.get()
        self.emulator.run_command(command, output_widget=self.output)
        self.entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    config_path = 'config.ini'
    emulator = Emulator(config_path)
    gui = ShellGUI(emulator)
    gui.run()