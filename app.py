from flask import Flask, request, render_template
from translate import translate_text, translate_vtt_content   # Funções de tradução
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    translated = None          # Valor que será mostrado na tela
    direction = "en-pt"      # padrão: Inglês -> Português

    if request.method == "POST":
        original = request.form.get("text", "")
        direction = request.form.get("direction", "en-pt")

        if original.strip():
            try:
                # Se o texto parece um VTT, preserve a estrutura e traduza apenas o conteúdo das legendas
                if re.search(r"^WEBVTT", original, re.I) or re.search(r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}", original):
                    translated = translate_vtt_content(original, direction=direction)
                else:
                    # texto simples — traduz e limpa pequenos artefatos
                    translated = translate_text(original, direction=direction)
                    translated = translated.replace("```", "").strip()

                    # remove prefixos comuns que o modelo às vezes antepõe
                    lines = translated.splitlines()
                    while lines and re.search(r"^(translation|tradução)\b[:\s-]*", lines[0].strip(), re.I):
                        lines.pop(0)
                    if lines:
                        lines[0] = re.sub(r"^[A-Za-z]+:\s*", "", lines[0])
                    translated = "\n".join(lines).strip()

            except Exception as e:
                translated = f"[Erro] {e}"

    return render_template("index.html", translated=translated, direction=direction)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
