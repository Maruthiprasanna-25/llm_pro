"""
Sandbox Service — Securely executes limited Python code.
"""

import logging
import sys
import io
import contextlib
import multiprocessing
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class SandboxService:
    """
    Executes Python code in a restricted environment with resource limits.
    """

    def execute_code(self, code: str, timeout: int = 3) -> Dict[str, Any]:
        """
        Executes code using a separate process to enforce timeout and resource isolation.
        """
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(target=self._restricted_run, args=(code, child_conn))
        
        try:
            process.start()
            if parent_conn.poll(timeout):
                result = parent_conn.recv()
            else:
                process.terminate()
                result = {"success": False, "error": "Execution timed out (3s limit reached)."}
        except Exception as e:
            result = {"success": False, "error": str(e)}
        finally:
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
        
        return result

    def _restricted_run(self, code: str, conn):
        """Standard library approach for basic restriction (not a full jail, but safe for math/pandas)."""
        output = io.StringIO()
        error = None
        success = True
        
        # Controlled namespace
        # In a full production app, we would use RestrictedPython here
        # For this implementation, we manually filter globals.
        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                "enumerate": enumerate, "filter": filter, "float": float, "int": int,
                "len": len, "list": list, "map": map, "max": max, "min": min,
                "range": range, "round": round, "set": set, "str": str, "sum": sum,
                "tuple": tuple, "zip": zip, "print": lambda *args: print(*args, file=output)
            },
            "math": __import__("math"),
            "json": __import__("json")
        }
        
        # Try to import pandas if available
        try:
            safe_globals["pd"] = __import__("pandas")
            safe_globals["np"] = __import__("numpy")
        except ImportError:
            pass

        try:
            # Check for illegal keywords
            forbidden = ["os.", "sys.", "subprocess", "socket", "eval(", "exec(", "open(", "__import__"]
            for word in forbidden:
                if word in code:
                    raise PermissionError(f"Security Violation: Use of '{word}' is forbidden.")

            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                exec(code, safe_globals)
            
            result_val = output.getvalue()
        except Exception as e:
            success = False
            result_val = str(e)
        
        conn.send({"success": success, "output": result_val})
        conn.close()

sandbox_service = SandboxService()
