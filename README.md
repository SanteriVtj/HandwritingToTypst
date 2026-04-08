# Handwriting to Typst CLI

A CLI tool that uses Ollama and Vision LMMs (like `llava`) to translate a folder of handwritten notes into a single Typst document.

## Features
- Scans a directory for images (`.png`, `.jpg`, `.jpeg`, `.webp`) and **PDF files**.
- Automatically converts PDF pages into images for processing.
- Converts handwriting to Typst markup using Ollama models.
- Consolidates all notes into a single `.typ` file.
- Easy to use with Docker.

## Prerequisites
- [Ollama](https://ollama.com/) installed and running.
- A vision-capable model pulled in Ollama (e.g., `ollama pull llava`).
- Docker (optional but recommended).

## Usage with Docker

### 1. Build the image
```bash
docker build -t handwriting-to-typst .
```

### 2. Run the tool
You'll need to mount your notes directory and specify the Ollama host (use `host.docker.internal` on macOS/Windows or the host IP on Linux).

```bash
docker run --rm \
  -v ./my_notes:/data \
  handwriting-to-typst \
  /data/input_folder /data/output.typ \
  --host http://host.docker.internal:11434
```

## Local Setup (without Docker)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the script
```bash
python main.py ./notes output.typ
```

## CLI Options
- `INPUT_DIR`: Path to folder containing image notes.
- `OUTPUT_FILE`: Path to save the resulting Typst file.
- `--model`: Ollama model to use (default: `llava`).
- `--host`: Ollama host URL (default: `http://localhost:11434`).
- `--prompt`: Custom prompt to override the default.
