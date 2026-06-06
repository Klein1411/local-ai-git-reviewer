# git-ai (Local AI Git Reviewer)

Một CLI tool mạnh mẽ bằng Python giúp tự động hóa quá trình review code và viết commit message chuẩn Conventional Commits. Công cụ này chạy 100% offline sử dụng Local LLM thông qua Ollama, bảo vệ hoàn toàn quyền riêng tư cho source code của bạn.

Được tối ưu hóa cho model **Qwen 2.5:3b** chạy mượt mà trên các máy có 4GB VRAM.

## Tính năng nổi bật

- 🚀 **Nhanh & Riêng tư:** Chạy hoàn toàn trên máy local, không cần mạng, không lo rò rỉ code.
- 🧹 **Smart Ignore:** Tự động loại bỏ các file lock (`.lock`), binary (`.png`, `.exe`...) để tiết kiệm Context Window.
- 📜 **Structured JSON:** Ép model trả về định dạng JSON chặt chẽ, loại bỏ hoàn toàn các câu chat nhảm của AI.
- 💬 **Interactive Commit:** Review commit message trước, nhấn `Y` để tự động chạy `git commit`.
- 🔍 **Ping & Auto-Pull:** Tự động kiểm tra trạng thái của Ollama và gợi ý tải model nếu chưa có.

## Hướng dẫn Cài đặt

### Bước 1: Setup Môi trường Ollama
1. Chạy script `install_env.ps1` (Right-click -> Run with PowerShell) để thiết lập biến môi trường `OLLAMA_MODELS` trỏ sang ổ D (tiết kiệm ổ C).
2. Tải và cài đặt Ollama từ [ollama.com](https://ollama.com/download/OllamaSetup.exe).
3. Mở Terminal mới, chạy lệnh tải model:
   ```bash
   ollama pull qwen2.5:3b
   ```

### Bước 2: Cài đặt git-ai CLI
Cài đặt project dưới dạng một CLI tool thực thụ trên máy:

```bash
cd D:\local-ai-git-reviewer
# Cài đặt công cụ pipx (nếu máy tính của bạn chưa có)
pip install pipx
pipx ensurepath

# Dùng pipx để cài đặt tool (pipx sẽ tự động tạo một venv an toàn và ngầm định)
pipx install -e .
```

## Hướng dẫn Sử dụng

Đầu tiên, bạn cần `git add` các file muốn commit.

**1. Tự động viết Commit Message:**
```bash
git-ai commit
```
Công cụ sẽ đọc diff, đề xuất một commit message tuyệt đẹp, và hỏi bạn có muốn commit luôn không `[Y/n]`.

**2. Review Code trước khi Commit:**
```bash
git-ai review
```
Công cụ sẽ quét lỗi tiềm ẩn, code smell, và hiển thị mức độ nghiêm trọng (High/Medium/Low) rất trực quan.

## Tùy biến Model
Nếu bạn có máy tính mạnh hơn (ví dụ: 8GB VRAM) và muốn đổi sang model `qwen2.5:7b` hoặc `llama3.1`, chỉ cần thêm flag `--model`:
```bash
git-ai commit --model qwen2.5:7b
```
