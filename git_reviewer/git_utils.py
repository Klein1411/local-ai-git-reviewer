import subprocess
from typing import List

# Các pattern rác thường gặp không mang giá trị ngữ nghĩa cho LLM
IGNORE_EXTENSIONS = [
    ".lock", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf",
    ".zip", ".tar", ".gz", ".mp3", ".mp4", ".bin", ".exe", ".dll", ".so",
    ".pyc", ".class"
]

IGNORE_FILES = [
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock"
]

def get_staged_files() -> List[str]:
    """Lấy danh sách các file đang được staged trong git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]
    except subprocess.CalledProcessError:
        return []

def is_ignored(filename: str) -> bool:
    """Kiểm tra xem file có thuộc diện bị ignore không."""
    if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return True
    
    # Lấy tên file gốc (bỏ đường dẫn)
    basename = filename.split("/")[-1].split("\\")[-1]
    if basename in IGNORE_FILES:
        return True
        
    return False

def get_staged_diff() -> str:
    """
    Lấy diff nội dung của các file đang staged.
    Loại bỏ các file bị ignore để tiết kiệm context window.
    """
    staged_files = get_staged_files()
    valid_files = [f for f in staged_files if not is_ignored(f)]
    
    if not valid_files:
        return ""
    
    try:
        # Lấy diff chỉ cho các file hợp lệ
        cmd = ["git", "diff", "--cached", "--"] + valid_files
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""
