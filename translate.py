# translate.py
import os
import re
import ollama

# 1️⃣ Defina a URL do Ollama (ou deixe a variável de ambiente já configurada)
OLLAMA_URL = "http://127.0.0.1:11434"

# 2️⃣ Informe ao cliente Python onde o Ollama está escutando
# (opção 1: variável de ambiente – funciona tanto no console quanto no Flask)
os.environ["OLLAMA_HOST"] = OLLAMA_URL

# Se preferir, pode usar a outra forma (instanciar o cliente diretamente):
# from ollama import Ollama
# ollama_client = Ollama(url=OLLAMA_URL)

def translate_text(text: str, direction: str = "en-pt", model: str = "llama3") -> str:
    """
    Envia `text` para Ollama e devolve a resposta (texto traduzido).

    :param text:  O texto em inglês que você quer traduzir.
    :param model: Nome do modelo (padrão: "llama3").
    :return: Texto traduzido para Português (pt-BR).
    """
    # 3️⃣ Use o método `chat` **sem** o parâmetro `url`
    # Defina a instrução do sistema dependendo da direção selecionada
    if direction == "en-pt":
        system_prompt = (
            "You are a helpful assistant that translates English to Brazilian Portuguese (pt-BR) "
            "and returns ONLY the translated text, without explanations or extra commentary."
        )
    else:
        system_prompt = (
            "You are a helpful assistant that translates Portuguese (pt-BR) to English "
            "and returns ONLY the translated text, without explanations or extra commentary."
        )

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    # `response["message"]["content"]` contém o texto gerado
    return response["message"]["content"].strip()


def translate_vtt_content(vtt_text: str, direction: str = "en-pt", model: str = "llama3") -> str:
    """Traduz o conteúdo de um arquivo VTT mantendo a estrutura (WEBVTT, índices, timestamps).

    - Detecta o cabeçalho `WEBVTT` e metadados iniciais.
    - Para cada bloco de legendas, preserva número e timestamp e traduz apenas o texto da legenda.
    - Tenta distribuir a tradução em múltiplas linhas quando o bloco original tem múltiplas linhas.
    """
    lines = vtt_text.splitlines()
    out_lines: list[str] = []
    i = 0

    # Cabeçalho WEBVTT
    if i < len(lines) and lines[0].strip().upper().startswith("WEBVTT"):
        out_lines.append(lines[0])
        i = 1
        # copia metadados até a primeira linha em branco
        while i < len(lines) and lines[i].strip() != "":
            out_lines.append(lines[i])
            i += 1
        if i < len(lines) and lines[i].strip() == "":
            out_lines.append("")
            i += 1

    ts_re = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")

    while i < len(lines):
        # lê um bloco até linha em branco
        block = []
        while i < len(lines) and lines[i].strip() != "":
            block.append(lines[i])
            i += 1

        if not block:
            # bloco vazio — mantém
            out_lines.append("")
        else:
            # procura linha de timestamp
            ts_idx = None
            for idx, l in enumerate(block):
                if ts_re.search(l):
                    ts_idx = idx
                    break

            if ts_idx is None:
                # sem timestamp — copia como está
                out_lines.extend(block)
            else:
                # copia possíveis linhas antes do timestamp (ex.: índice)
                for b in block[:ts_idx + 1]:
                    out_lines.append(b)

                text_lines = block[ts_idx + 1 :]
                original_count = max(1, len(text_lines))
                cue_text = " ".join([t.strip() for t in text_lines if t.strip()])

                if cue_text == "":
                    translated = ""
                else:
                    translated = translate_text(cue_text, direction=direction, model=model).strip()

                # distribui a tradução em múltiplas linhas seguindo sentenças, quando possível
                if original_count > 1:
                    parts = re.split(r'(?<=[.!?])\s+', translated)
                    if len(parts) >= original_count:
                        # agrupa partes para criar o mesmo número de linhas
                        per = max(1, len(parts) // original_count)
                        new_lines = []
                        idxp = 0
                        for _ in range(original_count):
                            take = parts[idxp: idxp + per]
                            if not take:
                                take = parts[idxp: idxp + 1]
                            new_lines.append(" ".join(take).strip())
                            idxp += per
                        if idxp < len(parts):
                            new_lines[-1] = (new_lines[-1] + " " + " ".join(parts[idxp:])).strip()
                    else:
                        new_lines = parts + [parts[-1]] * (original_count - len(parts))
                else:
                    new_lines = [translated]

                out_lines.extend(new_lines)

        # pula a linha em branco separadora
        if i < len(lines) and lines[i].strip() == "":
            out_lines.append("")
            i += 1

    # garante newline final
    return "\n".join(out_lines).rstrip() + "\n"
