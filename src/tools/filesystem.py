import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil

from src.core.chain import load_training_data, save_training_data, TrainingExample


ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".json", ".yaml", ".yml", ".xml", ".csv",
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".swift", ".kt", ".rb", ".php", ".html",
    ".css", ".scss", ".sql", ".sh", ".bash", ".zsh",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp3", ".mp4",
    ".zip", ".tar", ".gz", ".rar", ".env", ".gitignore",
    "README", "LICENSE", "Makefile", "Dockerfile", ".dockerignore"
}

BLOCKED_PATHS = {
    "/System", "/Library/Caches", "/private",
    "/Applications/.Trashes", "/Users/vyakaranamsowmya/.Trash"
}


class FileSystemTool:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.home()
        self.current_dir = self.base_path

    def is_safe_path(self, path: str) -> bool:
        path_obj = Path(path).resolve()
        
        for blocked in BLOCKED_PATHS:
            if str(path_obj).startswith(blocked):
                return False
        
        try:
            path_obj.relative_to(self.base_path)
            return True
        except ValueError:
            return False

    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        try:
            target = (self.current_dir / path).resolve()
            
            if not self.is_safe_path(str(target)):
                return {"error": "Access denied: Path not allowed"}
            
            if not target.exists():
                return {"error": "Path does not exist"}
            
            if not target.is_dir():
                return {"error": "Not a directory"}
            
            items = []
            for item in sorted(target.iterdir()):
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else 0,
                        "modified": stat.st_mtime
                    })
                except PermissionError:
                    items.append({
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": 0,
                        "modified": 0,
                        "error": "Permission denied"
                    })
            
            return {
                "path": str(target),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": str(e)}

    def read_file(self, path: str, lines: int = 100) -> Dict[str, Any]:
        try:
            target = (self.current_dir / path).resolve()
            
            if not self.is_safe_path(str(target)):
                return {"error": "Access denied"}
            
            if not target.exists():
                return {"error": "File does not exist"}
            
            if not target.is_file():
                return {"error": "Not a file"}
            
            suffix = target.suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS and target.name not in ALLOWED_EXTENSIONS:
                return {
                    "error": f"File type not allowed: {suffix}",
                    "hint": "Text-based files are supported"
                }
            
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                content = ''.join(all_lines[:lines])
                has_more = len(all_lines) > lines
            
            return {
                "path": str(target),
                "content": content,
                "lines": len(all_lines),
                "has_more": has_more,
                "size": target.stat().st_size
            }
        except Exception as e:
            return {"error": str(e)}

    def search_files(self, query: str, path: str = ".") -> Dict[str, Any]:
        try:
            import os
            import fnmatch
            
            search_paths = []
            
            if path == ".":
                home = Path.home()
                search_paths = [
                    home / "Downloads",
                    home / "Desktop", 
                    home / "Documents"
                ]
            else:
                target = (self.current_dir / path).resolve()
                search_paths = [target]
            
            results = []
            query_lower = query.lower()
            max_depth = 3
            
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                
                for root, dirs, files in os.walk(search_path):
                    # Check depth
                    depth = root[len(str(search_path)):].count(os.sep)
                    if depth > max_depth:
                        dirs.clear()
                        continue
                    
                    # Check files
                    for name in files:
                        if query_lower in name.lower():
                            results.append({
                                "name": name,
                                "path": str(Path(root) / name),
                                "type": "file"
                            })
                            if len(results) >= 30:
                                break
                    
                    # Check directories
                    for name in dirs:
                        if query_lower in name.lower():
                            results.append({
                                "name": name,
                                "path": str(Path(root) / name),
                                "type": "dir"
                            })
                            if len(results) >= 30:
                                break
                    
                    if len(results) >= 30:
                        break
                
                if len(results) >= 30:
                    break
            
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def search_content(self, query: str, path: str = ".") -> Dict[str, Any]:
        try:
            target = (self.current_dir / path).resolve()
            
            if not self.is_safe_path(str(target)):
                return {"error": "Access denied"}
            
            results = []
            
            for item in target.rglob("*"):
                if not item.is_file():
                    continue
                if not self.is_safe_path(str(item)):
                    continue
                
                suffix = item.suffix.lower()
                if suffix not in ALLOWED_EXTENSIONS:
                    continue
                
                try:
                    with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            lines = content.split('\n')
                            matching_lines = [l for l in lines if query.lower() in l.lower()]
                            
                            results.append({
                                "name": item.name,
                                "path": str(item),
                                "matches": matching_lines[:3]
                            })
                except:
                    continue
                
                if len(results) >= 20:
                    break
            
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_file_info(self, path: str) -> Dict[str, Any]:
        try:
            target = (self.current_dir / path).resolve()
            
            if not self.is_safe_path(str(target)):
                return {"error": "Access denied"}
            
            if not target.exists():
                return {"error": "Path does not exist"}
            
            stat = target.stat()
            
            return {
                "name": target.name,
                "path": str(target),
                "type": "dir" if target.is_dir() else "file",
                "size": stat.st_size,
                "size_formatted": self._format_size(stat.st_size),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_readable": os.access(target, os.R_OK),
                "is_writable": os.access(target, os.W_OK),
                "extension": target.suffix
            }
        except Exception as e:
            return {"error": str(e)}

    def get_drives(self) -> Dict[str, Any]:
        try:
            if os.name == 'posix':
                if os.uname().sysname == 'Darwin':
                    volumes = ["/Volumes"]
                    drives = []
                    for v in volumes:
                        if os.path.exists(v):
                            drives.extend([f"{v}/{d}" for d in os.listdir(v) if not d.startswith('.')])
                    
                    return {
                        "drives": ["/Users/vyakaranamsowmya", "/"] + drives,
                        "home": str(Path.home())
                    }
                else:
                    return {
                        "drives": ["/"],
                        "home": str(Path.home())
                    }
            else:
                return {"drives": ["C:"], "home": str(Path.home())}
        except Exception as e:
            return {"error": str(e)}

    def change_directory(self, path: str) -> Dict[str, Any]:
        try:
            if path == "~":
                self.current_dir = Path.home()
            elif path == "..":
                self.current_dir = self.current_dir.parent
            elif path == "/":
                self.current_dir = Path("/")
            else:
                target = (self.current_dir / path).resolve()
                
                if not self.is_safe_path(str(target)):
                    return {"error": "Access denied"}
                
                if not target.exists():
                    return {"error": "Directory does not exist"}
                
                if not target.is_dir():
                    return {"error": "Not a directory"}
                
                self.current_dir = target
            
            return {
                "current_dir": str(self.current_dir),
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}

    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


class TerminalTool:
    def __init__(self, allowed_commands: List[str] = None):
        self.allowed_commands = allowed_commands or [
            "ls", "ls -la", "ls -l", "pwd", "date", "whoami",
            "cat", "head", "tail", "grep", "find", "which",
            "git status", "git log", "git diff", "git branch",
            "python3", "pip3", "npm", "node", "curl"
        ]

    def execute(self, command: str) -> Dict[str, Any]:
        try:
            parts = command.split()
            if not parts:
                return {"error": "Empty command"}
            
            base_cmd = parts[0]
            
            if any(base_cmd in cmd for cmd in self.allowed_commands):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "command": command,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "return_code": result.returncode
                }
            else:
                return {
                    "error": f"Command not allowed: {base_cmd}",
                    "allowed_commands": self.allowed_commands
                }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}


class CodeAnalyzer:
    def analyze_file(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            analysis = {
                "path": path,
                "total_lines": len(lines),
                "empty_lines": sum(1 for l in lines if not l.strip()),
                "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith('#')),
                "comment_lines": sum(1 for l in lines if l.strip().startswith('#')),
                "imports": [],
                "functions": [],
                "classes": []
            }
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')):
                    analysis["imports"].append(stripped)
                elif stripped.startswith('def '):
                    func_name = stripped[4:stripped.find('(')]
                    analysis["functions"].append(func_name)
                elif stripped.startswith('class '):
                    class_name = stripped[6:stripped.find('(')] if '(' in stripped else stripped[6:]
                    analysis["classes"].append(class_name)
            
            return analysis
        except Exception as e:
            return {"error": str(e)}


def get_desktop_path() -> str:
    return str(Path.home() / "Desktop")


def get_documents_path() -> str:
    return str(Path.home() / "Documents")


def get_downloads_path() -> str:
    return str(Path.home() / "Downloads")
