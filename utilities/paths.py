# utilities/paths.py
import os

APP_FOLDER = "MA1_Autograder"  # change name if you want

def workspace_root() -> str:
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    root = os.path.join(docs, APP_FOLDER)
    os.makedirs(root, exist_ok=True)
    return root

def ws_path(*parts) -> str:
    """Join onto workspace root and ensure parent dirs exist."""
    p = os.path.join(workspace_root(), *parts)
    parent = os.path.dirname(p)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return p

def ensure_dir(*parts) -> str:
    """Ensure a workspace directory exists, return its path."""
    p = os.path.join(workspace_root(), *parts)
    os.makedirs(p, exist_ok=True)
    return p
