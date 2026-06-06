import typer
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Optional

from .git_utils import get_staged_diff
from .llm_client import ping_ollama, check_model_exists, generate_json, DEFAULT_MODEL
from .prompts import COMMIT_JSON_SCHEMA, REVIEW_JSON_SCHEMA

app = typer.Typer(help="Local AI Git Reviewer & Commit Generator")
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
def commit(model: str = typer.Option(DEFAULT_MODEL, help="Tên model Ollama để sử dụng")):
    """Sinh ra commit message tự động từ nội dung các file đang staged."""
    verify_environment(model)
    
    diff = get_staged_diff()
    if not diff:
        console.print("[yellow]Không có thay đổi nào đang được staged (Vui lòng chạy `git add`).[/yellow]")
        return
        
    with console.status(f"[bold green]Đang nhờ {model} viết commit message...[/bold green]"):
        try:
            result = generate_json(COMMIT_JSON_SCHEMA, f"Nội dung Git diff:\n{diff}", model=model)
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
def review(model: str = typer.Option(DEFAULT_MODEL, help="Tên model Ollama để sử dụng")):
    """Đánh giá code (Review) các file đang staged."""
    verify_environment(model)
    
    diff = get_staged_diff()
    if not diff:
        console.print("[yellow]Không có thay đổi nào đang được staged để review.[/yellow]")
        return
        
    with console.status(f"[bold green]Đang nhờ {model} review code...[/bold green]"):
        try:
            result = generate_json(REVIEW_JSON_SCHEMA, f"Nội dung Git diff:\n{diff}", model=model)
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
