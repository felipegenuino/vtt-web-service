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

Uma pequena aplicação Flask que usa Ollama para traduzir o conteúdo de arquivos `.vtt` (legendagem) de Inglês → Português (pt-BR).

  ---

  ## ✅ O que este repositório contém

  ```
  vtt-web-service/
  ├── app.py                # Flask + rota web (formulário de tradução)
  ├── translate.py          # Chama Ollama para traduzir texto
  ├── templates/
  │   └── index.html        # Página principal com formulário
  ├── requirements.txt
  └── Dockerfile (opcional)
  ```

  ---

  ## 🧰 Pré‑requisitos

  - Python 3.11+ instalado
  - Ollama (opcional, se for usar o motor local) — veja sessão abaixo
  - Docker (opcional, para rodar tudo via docker-compose)

  ---

  ## 🚀 Como executar (recomendado: virtualenv)

  1. Clone / entre na pasta do projeto

  ```bash
  cd path/to/vtt-web-service
  ```

  2. Crie e ative um ambiente virtual

  - Windows (PowerShell):

  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  # Se houver política restritiva, execute uma vez:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  ```

  - WSL / macOS / Linux:

  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

  3. Instale as dependências

  ```bash
  pip install -r requirements.txt
  ```

  > Observação: se o `pip` instalar pacotes no diretório do usuário e avisar que `flask.exe` foi colocado em `%APPDATA%\Python\...\Scripts` (como aconteceu aqui), prefira usar um `venv` para evitar problemas com PATH.

  4. Configure o Ollama (se estiver usando localmente)

  - Inicie o Ollama local (ou use uma instância remota). Se for local e quiser puxar o modelo exemplo:

  ```bash
  # Exemplo: instalar o modelo llama3 (executar na máquina onde o Ollama roda)
  ollama pull llama3
  ```

  Defina a variável de ambiente para apontar ao host do Ollama (exemplo: PowerShell / WSL):

  - PowerShell:

  ```powershell
  $env:OLLAMA_HOST = 'http://localhost:11434'
  ```

  - WSL / bash:

  ```bash
  export OLLAMA_HOST='http://localhost:11434'
  ```

  5. Executando a aplicação

  - Modo simples (usa o bloco `if __name__ == '__main__'` do `app.py`):

  ```bash
  python app.py
  ```

  - Ou usando o CLI do Flask (recomendado quando quiser usar `flask run`):

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

  Abra http://localhost:5000 no navegador e teste.

---

## 🖥️ Nova UI: direção, copiar e salvar

- A interface agora permite escolher a direção da tradução (English → Português (pt-BR) ou Português → English).
- Depois de gerar a tradução, há dois botões:
    - **Copiar** — copia apenas o texto da tradução para a área de transferência.
    - **Salvar como .vtt** — baixa a tradução como um arquivo `.vtt`. Se o texto não começar com um cabeçalho `WEBVTT`, o app adiciona um cabeçalho simples `WEBVTT\n\n` automaticamente.

    - **Preservação de estrutura VTT** — se você colar o conteúdo de um arquivo `.vtt` (que contenha `WEBVTT` ou timestamps no formato `00:00:00.000 --> 00:00:01.000`), o aplicativo preserva índices e timestamps e traduz apenas as linhas de texto das legendas, mantendo a estrutura válida do arquivo `.vtt`.

---

  ---

  ## 🐳 Executando com Docker Compose (Ollama + web)

  Crie um `docker-compose.yml` (exemplo já no projeto anterior) que inicia o serviço `ollama` e o `web`.

  ```bash
  docker compose up --build
  ```

  O serviço web ficará disponível em http://localhost:5000.

  ---

  ## ⚠️ Problemas comuns / Soluções

  - "flask: The term 'flask' is not recognized": isso ocorre quando o executável `flask.exe` (pip) está instalado em `%APPDATA%\Python\...\Scripts` que não está no PATH. Soluções:

    - Use `python -m flask ...` para evitar depender do `flask.exe` no PATH.
    - Use um `venv` e ative-o (melhor prática).
    - Adicione a pasta de Scripts ao PATH (apenas se souber o que faz):

      ```powershell
      $env:PATH += ';C:\Users\USERNAME\AppData\Roaming\Python\Python314\Scripts'
      # Para persistir, use setx (atenção ao tamanho do PATH):
      # cmd /c "setx PATH "%PATH%;C:\Users\USERNAME\AppData\Roaming\Python\Python314\Scripts""
      ```

  - Erros de conexão com Ollama: verifique `OLLAMA_HOST`, se o serviço está em execução e se a porta (11434 por padrão) está aberta.

  ---

  ## 💡 Dicas rápidas

  - Trocar o modelo (ex.: usar outro nome em `translate.py`) é possível passando `model='nome_do_modelo'`.
  - Se quiser retornar o texto traduzido na tela em vez de forçar download, troque `send_file(...)` por:

  ```python
  from flask import Response
  return Response(out_path.read_text(), mimetype='text/plain')
  ```

  ---

  ## Contato / Contribuição

  Abra uma issue ou envie um pull request com melhorias — sugestões para melhorar o README são bem-vindas! ✅

  ---

  Boa sorte — se quiser, eu posso também adicionar um script `make run` ou `poetry`/`pipenv` para facilitar os comandos. Quer que eu faça isso agora? ✨


