import sys
import os

# Добавление пути к родительской директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from core import Emulator

class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.emulator = Emulator('config.ini')

    def test_run_ls_command(self):
        """
        Тест команды ls через run_command.
        """
        self.emulator.run_command('ls')
        output = self.emulator.ls()
        self.assertIn('startup.sh', output)

    def test_run_cd_command(self):
        """
        Тест команды cd через run_command.
        """
        self.emulator.run_command('cd var')
        self.assertTrue(self.emulator.current_dir.endswith('var/'))

    def test_uname_command(self):
        """
        Тест команды uname через run_command.
        """
        self.assertEqual(self.emulator.run_command('uname'), "UnixEmulator")


if __name__ == '__main__':
    unittest.main()