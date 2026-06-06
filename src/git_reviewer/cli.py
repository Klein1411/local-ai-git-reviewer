import typer
import subprocess
import sys
import os
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Optional

# Ép kiểu UTF-8 cho console Windows để chống lỗi UnicodeEncodeError khi in tiếng Việt
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from .git_utils import get_staged_diff
from .llm_client import ping_ollama, check_model_exists, generate_json, DEFAULT_MODEL
from .prompts import COMMIT_JSON_SCHEMA, REVIEW_JSON_SCHEMA

app = typer.Typer(
    help=(
        "Local AI Git Reviewer & Commit Generator.\n\n"
        "A privacy-first CLI tool that uses Local LLMs (Ollama) to review your staged git changes "
        "and generate Conventional Commits automatically.\n\n"
        "Environment Variables:\n"
        "  GIT_AI_LANG: Set to 'en' or 'vi' to change the AI output language (Default: 'vi')."
    )
)
console = Console()

def verify_environment(model: str = DEFAULT_MODEL):
    """Kiểm tra môi trường Ollama trước khi chạy logic chính."""
    if not ping_ollama():
        console.print("[bold red]Lỗi: Không thể kết nối tới Ollama API tại http://localhost:11434[/bold red]")
        console.print("Vui lòng đảm bảo bạn đã cài đặt và đang bật phần mềm Ollama.")
        raise typer.Exit(code=1)
        
    if not check_model_exists(model):
        console.print(f"[bold yellow]Cảnh báo: Không tìm thấy model '{model}' trên máy.[/bold yellow]")
        console.print(f"Bạn có thể chạy lệnh sau để tải model: [bold cyan]ollama pull {model}[/bold cyan]")
        raise typer.Exit(code=1)

@app.command()
def commit(
    model: str = typer.Option(DEFAULT_MODEL, help="The Ollama model to use for generation")
):
    """
    Generate a Conventional Commit message automatically from staged files.
    
    This command reads `git diff --cached`, ignores lock files and binaries, 
    and asks the AI to propose a commit message. You can accept it interactively [Y/n].
    
    Tip: Run `$env:GIT_AI_LANG="en"` in PowerShell to force English output.
    """
    verify_environment(model)
    
    diff = get_staged_diff()
    if not diff:
        unstaged = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if unstaged:
            if Confirm.ask("[yellow]Không có file nào đang được staged.[/yellow] Bạn có muốn tự động chạy `git add .` không?"):
                subprocess.run(["git", "add", "."], check=True)
                diff = get_staged_diff()
            else:
                return
        else:
            console.print("[yellow]Không có thay đổi code nào trong project để commit.[/yellow]")
            return
        
    with console.status(f"[bold green]Đang nhờ {model} viết commit message...[/bold green]"):
        try:
            lang = os.environ.get("GIT_AI_LANG", "vi")
            user_prompt = f"Ngôn ngữ bắt buộc (Language): {'Tiếng Việt' if lang.lower() == 'vi' else 'English'}.\n\nNội dung Git diff:\n{diff}"
            result = generate_json(COMMIT_JSON_SCHEMA, user_prompt, model=model)
        except Exception as e:
            console.print(f"[bold red]Lỗi khi gọi AI:[/bold red] {str(e)}")
            return
            
    if not result:
        console.print("[red]AI không trả về kết quả hợp lệ.[/red]")
        return
        
    # In ra message đẹp mắt
    title = result.get("title", "")
    body = result.get("body", "")
    full_message = f"{title}\n\n{body}"
    
    console.print(Panel(full_message, title="💡 Đề xuất Commit Message", border_style="cyan"))
    
    # Hỏi xác nhận (Interactive)
    if Confirm.ask("Bạn có muốn commit với message này không?"):
        try:
            subprocess.run(["git", "commit", "-m", title, "-m", body], check=True)
            console.print("[bold green]✅ Đã commit thành công![/bold green]")
        except subprocess.CalledProcessError:
            console.print("[bold red]❌ Lỗi khi chạy lệnh git commit.[/bold red]")
    else:
        console.print("[yellow]Đã hủy commit. Bạn có thể chỉnh sửa code hoặc chạy lại lệnh.[/yellow]")

@app.command()
def review(
    model: str = typer.Option(DEFAULT_MODEL, help="The Ollama model to use for generation")
):
    """
    Analyze staged files and provide a Code Review.
    
    The AI will scan for bugs, code smells, and logic errors, outputting a severity 
    rating (HIGH/MEDIUM/LOW) for each issue.
    
    Tip: Run `$env:GIT_AI_LANG="en"` in PowerShell to force English output.
    """
    verify_environment(model)
    
    diff = get_staged_diff()
    if not diff:
        unstaged = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if unstaged:
            if Confirm.ask("[yellow]Không có file nào đang được staged.[/yellow] Bạn có muốn tự động chạy `git add .` không?"):
                subprocess.run(["git", "add", "."], check=True)
                diff = get_staged_diff()
            else:
                return
        else:
            console.print("[yellow]Không có thay đổi code nào trong project để review.[/yellow]")
            return
        
    with console.status(f"[bold green]Đang nhờ {model} review code...[/bold green]"):
        try:
            lang = os.environ.get("GIT_AI_LANG", "vi")
            user_prompt = f"Ngôn ngữ bắt buộc (Language): {'Tiếng Việt' if lang.lower() == 'vi' else 'English'}.\n\nNội dung Git diff:\n{diff}"
            result = generate_json(REVIEW_JSON_SCHEMA, user_prompt, model=model)
        except Exception as e:
            console.print(f"[bold red]Lỗi khi gọi AI:[/bold red] {str(e)}")
            return
            
    # Hiển thị Tóm tắt
    console.print(Panel(result.get("summary", ""), title="📝 Tóm tắt thay đổi", border_style="blue"))
    
    # Hiển thị Issues
    issues = result.get("issues", [])
    if not issues:
        console.print("[bold green]✅ Không tìm thấy lỗi tiềm ẩn nào. Code rất sạch![/bold green]")
    else:
        console.print("[bold red]⚠️  Phát hiện một số vấn đề cần lưu ý:[/bold red]")
        for issue in issues:
            severity = issue.get("severity", "unknown").upper()
            color = "red" if severity == "HIGH" else "yellow" if severity == "MEDIUM" else "cyan"
            console.print(f"  - [{color}][{severity}][/{color}] {issue.get('file')}: {issue.get('description')}")
            
    # Hiển thị Praise
    praise = result.get("praise", "")
    if praise:
        console.print(f"\n[bold green]🌟 Điểm sáng:[/bold green] {praise}")

if __name__ == "__main__":
    app()
