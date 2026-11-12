import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_current_dir)
_backend_python_dir = os.path.join(_repo_root, "backend-python")
_backend_app_dir = os.path.join(_backend_python_dir, "app")

if _backend_python_dir not in sys.path:
    sys.path.insert(0, _backend_python_dir)

if os.path.isdir(_backend_app_dir) and _backend_app_dir not in __path__:
    __path__.append(_backend_app_dir)
