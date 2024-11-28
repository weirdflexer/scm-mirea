import yaml
import subprocess
from datetime import datetime
from pathlib import Path

def read_config(config_path):
    """Читает конфигурационный файл."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def get_git_commits(repo_path, start_date):
    """Получает список коммитов после заданной даты."""
    cmd = [
        "git",
        "-C", repo_path,
        "log",
        f"--since={start_date}",
        "--pretty=format:%H %ad",
        "--date=short",
        "--name-only"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    return result.stdout.strip().split("\n\n")

def parse_commits(raw_commits):
    """Парсит данные о коммитах и извлекает зависимости."""
    graph = {}
    for block in raw_commits:
        lines = block.split("\n")
        commit_info = lines[0].split()
        commit_hash = commit_info[0]
        files = lines[1:]
        for file in files:
            if file not in graph:
                graph[file] = []
            graph[file].append(commit_hash)
    return graph

def generate_plantuml(graph):
    """Создаёт представление PlantUML для графа."""
    lines = ["@startuml", "digraph G {"]
    for node, dependencies in graph.items():
        for dep in dependencies:
            lines.append(f'    "{dep}" -> "{node}"')
    lines.append("}")
    lines.append("@enduml")
    return "\n".join(lines)

def save_output(output_path, content):
    """Сохраняет результат в файл."""
    with open(output_path, "w") as file:
        file.write(content)

def main(config_path):
    """Основная функция."""
    config = read_config(config_path)
    repo_path = config["repository_path"]
    start_date = config["start_date"]
    output_path = config["output_path"]

    raw_commits = get_git_commits(repo_path, start_date)
    graph = parse_commits(raw_commits)
    plantuml_code = generate_plantuml(graph)
    save_output(output_path, plantuml_code)
    print("Граф зависимостей создан:")
    print(plantuml_code)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_конфигурационному_файлу>")
    else:
        main(sys.argv[1])
