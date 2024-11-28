import pytest
from main import parse_commits, generate_plantuml

def test_parse_commits():
    raw_commits = [
        "1234567 2024-01-01\nfile1.txt\nfile2.txt",
        "89abcde 2024-01-02\nfile1.txt\nfile3.txt"
    ]
    result = parse_commits(raw_commits)
    assert "file1.txt" in result
    assert "file2.txt" in result
    assert result["file1.txt"] == ["1234567", "89abcde"]

def test_generate_plantuml():
    graph = {"file1.txt": ["1234567", "89abcde"], "file2.txt": ["1234567"]}
    plantuml = generate_plantuml(graph)
    assert '@startuml' in plantuml
    assert '1234567 -> "file1.txt"' in plantuml
