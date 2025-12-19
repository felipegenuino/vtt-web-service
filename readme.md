# Quick‑Translate vtt-web-service

```
vtt-web-service/
├── app.py                # Flask + rotas
├── vtt_tradutor.py       # Funções de leitura/translate (do script anterior)
├── templates/
│   └── index.html        # Página principal
├── static/
│   └── js/
│       └── main.js       # JS (opcional, se usar fetch)
├── requirements.txt
└── Dockerfile (opcional)
```


## 1 Dependências
### Requirements.txt

```bash 
    Flask
    ollama
    Werkzeug==2.3.4     # para FileStorage
```

### Instale:

```bash
    python -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
```

## 2 Código do backend (app.py) 
```python
from flask import Flask, request, send_file, render_template, redirect, url_for, flash
from pathlib import Path
import os
import tempfile

# Importa a lógica de tradução do script que você já tem
from vtt_tradutor import translate_vtt  # <-- ajuste o nome do módulo

app = Flask(__name__)
app.secret_key = "supersecret"          # necessário para flash mensagens


@app.route("/")
def index():
    """Página inicial – formulário de upload."""
    return render_template("index.html")


@app.route("/translate", methods=["POST"])
def translate():
    """Recebe o arquivo VTT e devolve o traduzido."""
    if "file" not in request.files:
        flash("Nenhum arquivo enviado.", "danger")
        return redirect(url_for("index"))

    vtt_file = request.files["file"]

    if vtt_file.filename == "":
        flash("Arquivo vazio.", "danger")
        return redirect(url_for("index"))

    # Salva o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".vtt") as tmp_in:
        vtt_file.save(tmp_in.name)
        tmp_in_path = Path(tmp_in.name)

    # Nome do arquivo de saída
    out_name = Path(vtt_file.filename).stem + "_traduzido.vtt"
    out_path = Path(tempfile.gettempdir()) / out_name

    try:
        # Chama a função de tradução (pode trocar o modelo aqui)
        translate_vtt(tmp_in_path, out_path, model="llama3")
    except Exception as e:
        flash(f"Erro ao traduzir: {e}", "danger")
        return redirect(url_for("index"))

    # Retorna o arquivo como download
    return send_file(
        out_path,
        as_attachment=True,
        download_name=out_name,
        mimetype="text/plain",
    )


if __name__ == "__main__":
    # O backend pode rodar em 127.0.0.1:5000 por padrão
    # Se usar Docker, exponha a porta 5000
    app.run(host="0.0.0.0", port=5000, debug=True)

```
 
> Dica – Se quiser mostrar o texto traduzido no próprio navegador (sem download), troque o send_file por return Response(out_path.read_text(), mimetype="text/plain").

## 3 Template HTML (templates/index.html)
```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Tradutor VTT</title>
  <!-- Bootstrap CDN -->
  // filepath: c:\Users\felip\Developer\vtt-web-service\readme.md
# Quick‑Translate — vtt-web-service 🚀

A small Flask application that uses Ollama to translate the contents of `.vtt` subtitle files between English and Brazilian Portuguese (pt-BR).

  ---

## ✅ What this repository contains

```
vtt-web-service/
├── app.py                # Flask web app (simple translation form)
├── translate.py          # Calls Ollama and contains VTT-aware translation logic
├── templates/
│   └── index.html        # Main UI (form, buttons)
├── requirements.txt
├── run.ps1               # PowerShell helper script to create venv and run the app
├── run.sh                # Bash helper script to create venv and run the app
└── Dockerfile (optional)
```

  ---

## 🧰 Prerequisites

- Python 3.11+ installed
- Ollama (optional, if you want to use a local Ollama instance) — see below
- Docker (optional, to run everything with docker-compose)

  ---

## 🚀 How to run (recommended: virtualenv)

1. Change into the project folder

```bash
cd path/to/vtt-web-service
```

2. Create and activate a virtual environment

- Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# If you have a restrictive execution policy, run once:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

- WSL / macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

Note: If `pip` warns that `flask.exe` was installed into `%APPDATA%\Python\...\Scripts`, prefer using the included `venv` to avoid PATH issues.

4. Configure Ollama (if using a local instance)

Start Ollama locally (or use a remote instance). To pull the example model:

```bash
# Example: pull the llama3 model on the machine running Ollama
ollama pull llama3
```

Set the `OLLAMA_HOST` environment variable to the host where Ollama is running (PowerShell / WSL):

- PowerShell:

```powershell
$env:OLLAMA_HOST = 'http://localhost:11434'
```

- WSL / bash:

```bash
export OLLAMA_HOST='http://localhost:11434'
```

5. Start the application

- Simple mode (uses `if __name__ == '__main__'` in `app.py`):

```bash
python app.py
```

- Or use Flask CLI (recommended for `flask run`):

PowerShell:

```powershell
$env:FLASK_APP='app.py'
python -m flask run --host=0.0.0.0 --port=5000
```

WSL / bash:

```bash
export FLASK_APP=app.py
python -m flask run --host=0.0.0.0 --port=5000
```

Open http://localhost:5000 in your browser and test.

---

## 🖥️ Nova UI: direção, copiar e salvar

- A interface agora permite escolher a direção da tradução (English → Português (pt-BR) ou Português → English).
- Depois de gerar a tradução, há dois botões:
    - **Copiar** — copia apenas o texto da tradução para a área de transferência.
    - **Salvar como .vtt** — baixa a tradução como um arquivo `.vtt`. Se o texto não começar com um cabeçalho `WEBVTT`, o app adiciona um cabeçalho simples `WEBVTT\n\n` automaticamente.

    - **Preservação de estrutura VTT** — se você colar o conteúdo de um arquivo `.vtt` (que contenha `WEBVTT` ou timestamps no formato `00:00:00.000 --> 00:00:01.000`), o aplicativo preserva índices e timestamps e traduz apenas as linhas de texto das legendas, mantendo a estrutura válida do arquivo `.vtt`.

---

  ---

## 🐳 Running with Docker Compose (Ollama + web)

Create a `docker-compose.yml` (see examples above) that runs an `ollama` service and the `web` service, then:

```bash
docker compose up --build
```

The web service will be available at http://localhost:5000.

  ---

## ⚠️ Common problems / Troubleshooting

- "flask: The term 'flask' is not recognized": this happens when the `flask.exe` created by pip was installed into `%APPDATA%\Python\...\Scripts` which is not in your PATH. Fixes:

    - Use `python -m flask ...` to avoid relying on `flask.exe` in PATH.
    - Use a `venv` and activate it (recommended).
    - Add the Scripts folder to your PATH (only if you know what you're doing):

        ```powershell
        $env:PATH += ';C:\Users\USERNAME\AppData\Roaming\Python\Python314\Scripts'
        # To persist, use setx (be careful with PATH length):
        # cmd /c "setx PATH "%PATH%;C:\Users\USERNAME\AppData\Roaming\Python\Python314\Scripts""
        ```

- Ollama connection errors: check `OLLAMA_HOST`, make sure the service is running and the port (11434 by default) is open.

  ---

## 💡 Quick tips

- To switch model (for example, use another model name in `translate.py`) pass `model='model_name'`.
- If you prefer to display the translated text in the browser instead of forcing a file download, return the content as a `Response`:

```python
from flask import Response
return Response(out_path.read_text(), mimetype='text/plain')
```

  ---

## Contributing

Open an issue or send a pull request with improvements — suggestions to improve this README and the app are welcome! ✅

---

If you want, I can add helper targets (e.g. a `make run`, or a `poetry`/`pipenv` setup) to make common tasks easier — would you like me to add one of those?


