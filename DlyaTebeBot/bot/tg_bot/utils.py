import re

_SPECIALS = r'[\[\]\(\)~`>#+\-=|{}.!]'  # якщо не використовуєш * і _, додай їх теж

_link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_codeblock_re = re.compile(r'```.*?```', re.S)
_inlinecode_re = re.compile(r'`[^`]*`')

def _escape_segment(seg: str) -> str:
    # 1) спочатку обробимо markdown-посилання: екрануємо текст в [] та дужки в URL
    def _fix_link(m):
        text, url = m.group(1), m.group(2)
        text_escaped = re.sub(r'([_*[\]()`>#+\-=|{}.!])', r'\\\1', text)  # тут вже можна екранувати * _
        url_escaped = url.replace("(", r"\(").replace(")", r"\)")
        return f'[{text_escaped}]({url_escaped})'

    seg = _link_re.sub(_fix_link, seg)

    # 2) екрануємо інші спецсимволи поза лінками
    seg = re.sub(rf'({_SPECIALS})', r'\\\1', seg)
    return seg

def mdv2_escape(text: str) -> str:
    if not text:
        return ""
    # Розіб’ємо на ділянки: код-блоки, інлайн-код, решта
    tokens = []
    idx = 0
    # знайдемо всі code blocks
    for m in _codeblock_re.finditer(text):
        before = text[idx:m.start()]
        if before:
            # всередині before ще приберемо інлайн-код
            last = 0
            for ic in _inlinecode_re.finditer(before):
                nb = before[last:ic.start()]
                if nb:
                    tokens.append(_escape_segment(nb))
                tokens.append(ic.group(0))  # інлайн-код як є
                last = ic.end()
            rest = before[last:]
            if rest:
                tokens.append(_escape_segment(rest))
        tokens.append(m.group(0))  # code block як є
        idx = m.end()
    tail = text[idx:]
    if tail:
        last = 0
        for ic in _inlinecode_re.finditer(tail):
            nb = tail[last:ic.start()]
            if nb:
                tokens.append(_escape_segment(nb))
            tokens.append(ic.group(0))
            last = ic.end()
        rest = tail[last:]
        if rest:
            tokens.append(_escape_segment(rest))

    return "".join(tokens)