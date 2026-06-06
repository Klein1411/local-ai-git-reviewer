# git-ai

A privacy-first, local CLI tool that uses Ollama to automatically review your staged git changes and generate Conventional Commits. It runs 100% offline, ensuring your source code never leaves your machine.

Optimized for small, efficient models like `qwen2.5:3b` to run smoothly on lower-end hardware (e.g., 4GB VRAM).

## Features

- **Offline First:** Operates entirely locally. No API keys required, no data sent to external servers.
- **Smart Ignore:** Automatically filters out lock files (`.lock`) and binaries to optimize context windows and prevent token waste.
- **Structured Output:** Enforces strict JSON responses from the LLM, eliminating conversational filler.
- **Interactive Commits:** Proposes a conventional commit message and allows you to apply it interactively.
- **Bilingual Support:** Outputs commit messages and reviews in English or Vietnamese via environment variables.

## Installation

### 1. Configure Ollama Environment

If you want to store Ollama models on a custom drive (e.g., D: drive) to save C: drive space, run the provided PowerShell script before installing Ollama:

```powershell
.\install_env.ps1
```

Download and install Ollama from [ollama.com](https://ollama.com/). Then, pull the recommended model:

```bash
ollama pull qwen2.5:3b
```

### 2. Install the CLI

It is highly recommended to install `git-ai` globally using `pipx` to isolate its dependencies.

```bash
cd local-ai-git-reviewer
pipx install -e .
```

## Usage

Stage your changes first:

```bash
git add <files>
```

### Generate a Commit Message

```bash
git-ai commit
```

The CLI will read your `git diff --cached`, propose a well-formatted conventional commit message, and prompt you for confirmation before executing `git commit`.

### Review Code

```bash
git-ai review
```

The CLI will analyze your staged code for potential bugs, logic errors, and code smells, categorized by severity (HIGH, MEDIUM, LOW).

### Configuration

#### Language Options

You can enforce the output language (English or Vietnamese) by setting the `GIT_AI_LANG` environment variable.

**PowerShell:**
```powershell
$env:GIT_AI_LANG="en"
git-ai commit
```

**Bash/Zsh:**
```bash
export GIT_AI_LANG="en"
git-ai commit
```

#### Custom Models

To use a different local model (e.g., `llama3.1`), pass the `--model` flag:

```bash
git-ai review --model llama3.1
```
