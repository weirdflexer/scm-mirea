import unittest
from unittest.mock import patch, mock_open
from datetime import datetime, timezone
from main import (
    read_config,
    read_git_object,
    parse_commit_object,
    get_files_from_tree,
    get_commits_since,
    parse_commits,
    generate_plantuml,
    save_output,
)

class TestGitDependencyGraph(unittest.TestCase):

    def test_parse_commits(self):
        commits = [
            {"hash": "hash1", "files": ["file1.txt"]},
            {"hash": "hash2", "files": ["file1.txt", "file2.txt"]},
        ]
        graph = parse_commits(commits)
        self.assertEqual(len(graph["file1.txt"]), 2)
        self.assertIn("hash1", graph["file1.txt"])
        self.assertIn("hash2", graph["file1.txt"])

    def test_generate_plantuml(self):
        graph = {
            "file1.txt": ["hash1", "hash2"],
            "file2.txt": ["hash2"],
        }
        plantuml_code = generate_plantuml(graph)
        self.assertIn("@startuml", plantuml_code)
        self.assertIn('"hash1" -> "file1.txt"', plantuml_code)
        self.assertIn('"hash2" -> "file2.txt"', plantuml_code)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_output(self, mock_file):
        save_output("/path/to/output.txt", "content")
        mock_file.assert_called_with("/path/to/output.txt", "w")
        mock_file().write.assert_called_with("content")

if __name__ == "__main__":
    unittest.main()
