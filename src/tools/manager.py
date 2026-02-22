from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import re
import os

from src.tools.filesystem import FileSystemTool, TerminalTool, CodeAnalyzer
from src.tools.filesystem import get_desktop_path, get_documents_path, get_downloads_path


@dataclass
class ToolResult:
    success: bool
    result: Any
    error: Optional[str] = None


class ToolManager:
    def __init__(self, base_path: str = None):
        self.file_system = FileSystemTool(base_path)
        self.terminal = TerminalTool()
        self.code_analyzer = CodeAnalyzer()
        
        self.folder_map = {
            "downloads": get_downloads_path(),
            "download": get_downloads_path(),
            "desktop": get_desktop_path(),
            "documents": get_documents_path(),
            "document": get_documents_path(),
            "home": os.path.expanduser("~"),
        }

    def detect_tool(self, query: str) -> Optional[tuple]:
        q = query.lower().strip()
        
        # Simple folder names
        if q in self.folder_map:
            return (self.change_directory, (self.folder_map[q],))
        
        # List files in folder - simple approach
        if "downloads" in q and ("list" in q or "show" in q or "files" in q or "what" in q):
            return (self.list_directory, (get_downloads_path(),))
        
        if "desktop" in q and ("list" in q or "show" in q or "files" in q or "what" in q):
            return (self.list_directory, (get_desktop_path(),))
        
        if "documents" in q and ("list" in q or "show" in q or "files" in q or "what" in q):
            return (self.list_directory, (get_documents_path(),))
        
        # Go to folder
        if q.startswith("go to "):
            folder = q.replace("go to ", "").strip()
            if folder in self.folder_map:
                return (self.change_directory, (self.folder_map[folder],))
        
        if q.startswith("cd "):
            folder = q.replace("cd ", "").strip()
            if folder in self.folder_map:
                return (self.change_directory, (self.folder_map[folder],))
        
        # Simple commands
        if q in ["ls", "list", "pwd", "drives"]:
            return (self.tools.get(q, self.list_directory), ())
        
        # Find files
        if q.startswith("find "):
            search_term = q.replace("find ", "").strip()
            return (self.search_files, (search_term,))
        
        # Search in files
        if q.startswith("search ") and "in" not in q:
            search_term = q.replace("search ", "").strip()
            return (self.search_files, (search_term,))
        
        # Grep
        if q.startswith("grep ") or (q.startswith("search ") and "in" in q):
            search_term = q.replace("grep ", "").replace("search in ", "").strip()
            return (self.search_content, (search_term,))
        
        # Read file
        if q.startswith("read ") or q.startswith("cat "):
            file_path = q.replace("read ", "").replace("cat ", "").strip()
            return (self.read_file, (file_path,))
        
        # Analyze code
        if q.startswith("analyze "):
            file_path = q.replace("analyze ", "").strip()
            return (self.analyze_code, (file_path,))
        
        # Run command
        if q.startswith("run ") or q.startswith("shell ") or q.startswith("!"):
            command = q.replace("run ", "").replace("shell ", "").strip()
            if command.startswith("!"):
                command = command[1:]
            return (self.run_command, (command,))
        
        return None

    def execute(self, query: str) -> ToolResult:
        intent = self.detect_tool(query)
        
        if intent:
            tool_func, args = intent
            try:
                return tool_func(*args)
            except Exception as e:
                return ToolResult(success=False, result=None, error=str(e))
        
        return ToolResult(
            success=False,
            result=None,
            error="Could not understand command"
        )

    def execute_full_search(self, query: str) -> ToolResult:
        """Search entire home directory for files/folders"""
        import os
        from pathlib import Path
        
        # Extract search term
        search_term = query.lower()
        for prefix in ['find ', 'search for ', 'search ', 'look for ', 'where is ', 'locate ']:
            search_term = search_term.replace(prefix, '').strip()
        
        if not search_term:
            search_term = query.lower().replace('find ', '').replace('search ', '').strip()
        
        results = []
        home = Path.home()
        max_results = 50
        
        # Search through entire home directory
        try:
            for root, dirs, files in os.walk(home):
                # Skip hidden and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'Library', 'Applications']]
                
                # Check directories
                for name in dirs:
                    if search_term.lower() in name.lower():
                        results.append({
                            "name": name,
                            "path": str(Path(root) / name),
                            "type": "dir"
                        })
                        if len(results) >= max_results:
                            break
                    
                    if len(results) >= max_results:
                        break
                
                # Check files
                for name in files:
                    if search_term.lower() in name.lower():
                        results.append({
                            "name": name,
                            "path": str(Path(root) / name),
                            "type": "file"
                        })
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
                    
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))
        
        return ToolResult(
            success=True,
            result={
                "query": search_term,
                "results": results,
                "count": len(results),
                "search_type": "full_system"
            }
        )

    def list_directory(self, path: str = ".") -> ToolResult:
        result = self.file_system.list_directory(path)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def change_directory(self, path: str = ".") -> ToolResult:
        result = self.file_system.change_directory(path)
        return ToolResult(
            success=result.get("success", False),
            result=result,
            error=result.get("error")
        )

    def get_current_dir(self) -> ToolResult:
        return ToolResult(
            success=True,
            result={"current_dir": str(self.file_system.current_dir)}
        )

    def read_file(self, path: str, lines: int = 50) -> ToolResult:
        result = self.file_system.read_file(path, lines)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def search_files(self, query: str, path: str = ".") -> ToolResult:
        result = self.file_system.search_files(query, path)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def search_content(self, query: str, path: str = ".") -> ToolResult:
        result = self.file_system.search_content(query, path)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def get_file_info(self, path: str) -> ToolResult:
        result = self.file_system.get_file_info(path)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def get_drives(self) -> ToolResult:
        result = self.file_system.get_drives()
        return ToolResult(success=True, result=result)

    def go_to_desktop(self) -> ToolResult:
        return self.change_directory(get_desktop_path())

    def go_to_documents(self) -> ToolResult:
        return self.change_directory(get_documents_path())

    def go_to_downloads(self) -> ToolResult:
        return self.change_directory(get_downloads_path())

    def analyze_code(self, path: str) -> ToolResult:
        result = self.code_analyzer.analyze_file(path)
        if "error" in result:
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    def run_command(self, command: str) -> ToolResult:
        result = self.terminal.execute(command)
        if "error" in result and "allowed" not in result.get("error", ""):
            return ToolResult(success=False, result=None, error=result["error"])
        return ToolResult(success=True, result=result)

    @property
    def tools(self):
        return {
            "ls": self.list_directory,
            "list": self.list_directory,
            "cd": self.change_directory,
            "pwd": self.get_current_dir,
            "cat": self.read_file,
            "read": self.read_file,
            "find": self.search_files,
            "search": self.search_files,
            "grep": self.search_content,
            "info": self.get_file_info,
            "drives": self.get_drives,
            "desktop": self.go_to_desktop,
            "documents": self.go_to_documents,
            "downloads": self.go_to_downloads,
            "analyze": self.analyze_code,
            "run": self.run_command,
            "shell": self.run_command,
        }

    def format_result(self, result: ToolResult) -> str:
        if not result.success:
            return f"❌ Error: {result.error}"
        
        data = result.result
        
        if "items" in data:
            output = f"📁 {data['path']}\n\n"
            for item in data["items"][:20]:
                icon = "📂" if item["type"] == "dir" else "📄"
                size = self._format_size(item["size"]) if item.get("size") else ""
                output += f"{icon} {item['name']} {size}\n"
            if data["count"] > 20:
                output += f"\n... and {data['count'] - 20} more items"
            return output
        
        if "content" in data:
            output = f"📄 {data['path']}\n"
            output += f"Lines: {data['lines']}"
            if data.get("has_more"):
                output += " (showing first 50)"
            output += f"\n\n{data['content'][:2000]}"
            return output
        
        if "results" in data:
            output = f"🔍 Search: {data.get('query', '')}\n\n"
            for item in data["results"][:10]:
                output += f"📄 {item['name']}\n   {item['path']}\n"
            output += f"\nFound: {data['count']} results"
            return output
        
        if "output" in data:
            return f"💻 Output:\n{data['output'][:1000]}"
        
        if "total_lines" in data:
            output = f"📊 Code Analysis: {data['path']}\n\n"
            output += f"Lines: {data['total_lines']}\n"
            output += f"Code: {data['code_lines']}\n"
            output += f"Comments: {data['comment_lines']}\n"
            if data.get("functions"):
                output += f"\nFunctions: {', '.join(data['functions'][:5])}"
            if data.get("classes"):
                output += f"\nClasses: {', '.join(data['classes'][:5])}"
            return output
        
        return str(data)
    
    def _format_size(self, size: int) -> str:
        if size == 0:
            return ""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"({size:.1f} {unit})"
            size /= 1024.0
        return f"({size:.1f} TB)"
