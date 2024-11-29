import yaml
from pathlib import Path
import zlib
import os
from datetime import datetime, timezone

def read_config(config_path):
    """Читает конфигурационный файл YAML."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def read_git_object(repo_path, object_hash):
    """Читает объект Git по его хэшу из директории .git/objects."""
    obj_path = os.path.join(repo_path, ".git", "objects", object_hash[:2], object_hash[2:])
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"Объект {object_hash} не найден по пути {obj_path}")
    with open(obj_path, "rb") as file:
        compressed_data = file.read()
        decompressed_data = zlib.decompress(compressed_data)
    return decompressed_data

def parse_commit_object(repo_path, commit_hash):
    """Парсит объект коммита, извлекает дерево, родителей, временную метку и файлы."""
    commit_data = read_git_object(repo_path, commit_hash)
    _, content = commit_data.split(b"\x00", 1)
    lines = content.decode().split("\n")

    tree_hash = next(line.split()[1] for line in lines if line.startswith("tree"))
    parent_hashes = [line.split()[1] for line in lines if line.startswith("parent")]
    author_line = next(line for line in lines if line.startswith("author"))
    timestamp = int(author_line.split()[-2])
    files = get_files_from_tree(repo_path, tree_hash)

    return {
        "tree": tree_hash,
        "parents": parent_hashes,
        "timestamp": timestamp,
        "files": files,
    }

def get_files_from_tree(repo_path, tree_hash, path_prefix=""):
    """Рекурсивно извлекает файлы из дерева Git."""
    tree_data = read_git_object(repo_path, tree_hash)
    _, content = tree_data.split(b"\x00", 1)
    files = []
    while content:
        null_idx = content.index(b"\x00")
        mode_name = content[:null_idx].decode()
        obj_hash = content[null_idx + 1 : null_idx + 21].hex()
        content = content[null_idx + 21 :]
        mode, name = mode_name.split(" ", 1)
        full_path = f"{path_prefix}/{name}" if path_prefix else name
        if mode == "40000":  # Дерево (папка)
            files.extend(get_files_from_tree(repo_path, obj_hash, full_path))
        else:  # Блоб (файл)
            files.append(full_path)
    return files

def get_commits_since(repo_path, start_date):
    """Получает все коммиты начиная с указанной даты."""
    head_ref_path = Path(repo_path, ".git", "refs", "heads", "main")
    if not head_ref_path.exists():
        raise FileNotFoundError(f"Файл ссылки HEAD не найден: {head_ref_path}")
    head_ref = head_ref_path.read_text().strip()

    commits = []
    to_visit = [head_ref]
    seen = set()

    while to_visit:
        commit_hash = to_visit.pop()
        if commit_hash in seen:
            continue
        seen.add(commit_hash)
        commit = parse_commit_object(repo_path, commit_hash)
        commit_date = datetime.fromtimestamp(commit["timestamp"], tz=timezone.utc)
        if commit_date < start_date:
            continue
        commits.append({
            "hash": commit_hash,
            "date": commit_date.strftime("%Y-%m-%d"),
            "files": commit["files"],
        })
        to_visit.extend(commit["parents"])

    return commits

def parse_commits(commits):
    """Создаёт граф зависимости файлов и коммитов."""
    graph = {}
    for commit in commits:
        commit_hash = commit["hash"]
        files = commit["files"]
        for file in files:
            if file not in graph:
                graph[file] = []
            graph[file].append(commit_hash)
    return graph

def generate_plantuml(graph):
    """Генерирует код PlantUML из графа."""
    lines = ["@startuml", "digraph G {"]
    for node, dependencies in graph.items():
        for dep in dependencies:
            lines.append(f'    "{dep}" -> "{node}"')
    lines.append("}")
    lines.append("@enduml")
    return "\n".join(lines)

def save_output(output_path, content):
    """Сохраняет контент в файл."""
    with open(output_path, "w") as file:
        file.write(content)

def main(config_path):
    """Основная функция для запуска обработки."""
    config = read_config(config_path)
    repo_path = config["repository_path"]
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    output_path = config["output_path"]

    commits = get_commits_since(repo_path, start_date)
    graph = parse_commits(commits)
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
