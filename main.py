import os
import click
import ollama
from PIL import Image
from pathlib import Path
import base64
from io import BytesIO
import fitz  # PyMuPDF

def process_content(client, model, prompt, images, filename, page_num=None):
    """Sends processing request to Ollama and formats output."""
    context = f"{filename} (Page {page_num})" if page_num is not None else filename
    click.echo(f"Processing {context}...")
    
    try:
        response = client.generate(
            model=model,
            prompt=prompt,
            images=images,
            stream=False
        )
        content = response.get('response', '').strip()
        # Basic cleanup in case the model ignored the instruction and added markdown blocks
        if content.startswith('```'):
            lines = content.splitlines()
            if lines[0].startswith('```'):
                content = "\n".join(lines[1:-1])
        
        return f"// --- From {context} ---\n{content}\n"
    except Exception as e:
        click.echo(f"Error processing {context}: {e}", err=True)
        return f"// ERROR processing {context}: {e}\n"

@click.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False), required=False)
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--model', default='llava', help='Name of the Ollama vision model to use.')
@click.option('--host', default='http://localhost:11434', help='Ollama host URL.')
@click.option('--prompt', default=None, help='Custom prompt for the LLM.')
@click.option('--list-models', is_flag=True, help='List available Ollama models and exit.')
def main(input_dir, output_file, model, host, prompt, list_models):
    """
    Translates handwritten notes (images/PDFs) in INPUT_DIR to Typst markup and saves to OUTPUT_FILE.
    """
    client = ollama.Client(host=host)
    
    if list_models:
        try:
            models = client.list()
            click.echo("Available Ollama models:")
            for m in models.get('models', []):
                click.echo(f" - {m['name']}")
        except Exception as e:
            click.echo(f"Error connecting to Ollama at {host}: {e}", err=True)
        return

    if not input_dir or not output_file:
        click.echo("Error: Missing arguments 'INPUT_DIR' and 'OUTPUT_FILE'. Use --help for usage.")
        return
    
    # Get all supported files and sort them
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    pdf_extension = '.pdf'
    all_extensions = img_extensions + (pdf_extension,)
    
    file_paths = sorted([
        p for p in Path(input_dir).iterdir() 
        if p.suffix.lower() in all_extensions
    ])
    
    if not file_paths:
        click.echo(f"No supported files (images or PDFs) found in {input_dir}")
        return

    default_prompt = (
        "You are an expert OCR and Typst formatter. "
        "Convert the following handwritten note into clean Typst markup. "
        "Focus on maintaining the structure, equations, and formatting. "
        "Return ONLY the Typst code, NO markdown blocks, NO preamble, and NO explanation."
    )
    
    final_prompt = prompt if prompt else default_prompt
    
    click.echo(f"Found {len(file_paths)} files. Starting conversion using model '{model}'...")
    
    for file_path in file_paths:
        if file_path.suffix.lower() == pdf_extension:
            try:
                doc = fitz.open(str(file_path))
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    result = process_content(client, model, final_prompt, [img_bytes], file_path.name, page_num + 1)
                    
                    # Open, append, and close for every page
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(result + "\n")
                doc.close()
            except Exception as e:
                click.echo(f"Failed to open PDF {file_path.name}: {e}", err=True)
        else:
            # Standard image
            result = process_content(client, model, final_prompt, [str(file_path)], file_path.name)
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(result + "\n")
    
    click.echo(f"\nSuccessfully created {output_file}")

if __name__ == '__main__':
    main()
