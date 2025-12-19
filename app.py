from flask import Flask, request, render_template, jsonify
from translate import translate_text, translate_vtt_content   # Funções de tradução
import re

# Top 7 most used languages (by number of speakers) and additional common languages
LANGUAGES_TOP = [
    ("zh-CN", "Chinese (Simplified)"),
    ("es", "Spanish"),
    ("en", "English"),
    ("hi", "Hindi"),
    ("ar", "Arabic"),
    ("bn", "Bengali"),
    ("pt-BR", "Portuguese (Brazil)")
]

LANGUAGES_OTHER = [
    ("fr", "French"),
    ("de", "German"),
    ("it", "Italian"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("ru", "Russian"),
    ("ar", "Arabic")
]

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    translated = None          # Valor que será mostrado na tela
    # defaults
    source_lang = "auto"
    target_lang = "pt-BR"

    if request.method == "POST":
        original = request.form.get("text", "")
        source_lang = request.form.get("source_lang", source_lang)
        target_lang = request.form.get("target_lang", target_lang)

        if original.strip():
            try:
                # Se o texto parece um VTT, preserve a estrutura e traduza apenas o conteúdo das legendas
                if re.search(r"^WEBVTT", original, re.I) or re.search(r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}", original):
                    translated = translate_vtt_content(original, direction=f"{source_lang}-{target_lang}")
                else:
                    # texto simples — traduz e limpa pequenos artefatos
                    translated = translate_text(original, source_lang=source_lang, target_lang=target_lang)
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

    # convenience: direction shorthand for templates (e.g. 'en-pt')
    direction = f"{source_lang}-{target_lang}"
    return render_template(
        "index.html",
        translated=translated,
        direction=direction,
        source_lang=source_lang,
        target_lang=target_lang,
        languages_top=LANGUAGES_TOP,
        languages_other=LANGUAGES_OTHER,
    )


@app.route('/detect-language', methods=['POST'])
def detect_language():
    """Detect language for pasted text. Returns a language code suggestion and display name."""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not text or len(text.strip()) < 3:
        return jsonify({'ok': False, 'error': 'text too short'}), 400

    # lightweight detection (uses langdetect)
    try:
        from langdetect import detect_langs
        probs = detect_langs(text)
        if not probs:
            raise ValueError('no detection')
        top = probs[0]
        code = top.lang
        confidence = float(top.prob)
    except Exception:
        return jsonify({'ok': False, 'error': 'detection failed', 'confidence': 0.0}), 500

    # Normalize some codes
    mapping = {
        'zh': 'zh-CN',
        'pt': 'pt-BR',
    }
    code_norm = mapping.get(code, code)

    # friendly name lookup
    name_map = {k: v for k, v in LANGUAGES_TOP + LANGUAGES_OTHER}
    display = name_map.get(code_norm, code_norm)

    return jsonify({'ok': True, 'code': code_norm, 'display': display, 'confidence': confidence})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
