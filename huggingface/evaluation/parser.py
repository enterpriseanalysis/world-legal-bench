"""Deterministic multilingual final-choice extraction; see docs/evaluation.md."""

import re

PARSER_VERSION = "world-legal-final-choice-v1.3"

# Match declarations, not an arbitrary A-D mentioned in an explanation. Keep
# case-insensitivity scoped to words: the option itself must be uppercase ASCII.
_FINAL_LABEL = r"""(?ix:
    (?:(?:the\s+)?(?:(?:correct|best|final)\s+
        (?:answer|response|assessment|statement|conclusion|option|choice)
        |answer|response|assessment|statement|conclusion))
    |(?:la\s+)?(?:(?:bonne\s+)?(?:réponse|proposition|analyse|conclusion|solution|combinaison)
        (?:\s+(?:correcte|exacte|fondée|attendue|conforme|permise|la\s+plus\s+correcte))?)
    |(?:a\s+)?(?:resposta(?:\s+institucional)?|alternativa|orientação|conclusão|avaliação|leitura|sequência|afirmação)
        (?:\s+(?:correta|adequada))?
    |(?:la\s+)?(?:respuesta|opción|conclusión|combinación|valoración|solución|actuación|secuencia)
        (?:\s+(?:correcta|adecuada))?
    |(?:jawaban|penilaian|kesimpulan|paket\s+prosedur)(?:\s+yang\s+(?:paling\s+)?(?:tepat|benar|sesuai|mendekati))?
    |(?:सही\s+)?(?:उत्तर|विकल्प|निष्कर्ष|कथन|आकलन)
    |(?:(?:正确|准确)\s*)?(?:答案|选项|判断|结论|评价|处理|项)|应选|符合规定的是|应采取的步骤
    |正解|答え|回答|結論|(?:正しい|適切な)(?:説明|評価|もの|整理|取扱い|判断|対応)|正しいの|適切なの
    |정답|(?:옳은|올바른)\s*(?:판단|설명|답변)|결론|최종\s+답변
)"""
_FINAL_START = (
    r"(?m)(?:^[ \t]*|(?<=[.;。।!?])[ \t]+)"
    r"(?:(?i:therefore|thus|so|hence|donc|portanto|por tanto|jadi|अतः|综上|因此)"
    r"(?:[ \t]*[,，:：][ \t]*|[ \t]+))?"
    r"(?:(?i:based on the text provided),[ \t]+|"
    r"प्रश्न के शब्दों[^\n]{0,120}के आधार पर[ \t]+|निकटतम/)?"
)
_OPTION_END = r"(?=$|[\s).。।:：、,;!?/（]|입니다|です|が|로|을|를)"
_FINAL_DECLARATION = re.compile(
    _FINAL_START + _FINAL_LABEL
    # Ordinary nouns followed by a letter can be option discussion (e.g.
    # 'La proposition A serait vraie si ...'). Require a declarative connector
    # or colon. Hindi's direct 'सही विकल्प A है' has its own branch below.
    + r"(?i:(?:[ \t]*(?:is|est|é|es|adalah|है|是|为|は|은|는)[ \t]*[:：]?\s*"
      r"|[ \t]*[:：]\s*)"
      r"(?:(?:(?-i:a)|la|the)[ \t]+)?"
      r"(?:(?:alternativa|opción|option|विकल्प|सबसे[ \t]+उपयुक्त[ \t]+विकल्प)\s+)?)"
      r"\(?([A-D])" + _OPTION_END
)
_FINAL_DIRECT = re.compile(
    _FINAL_START + r"(?:सही[ \t]+(?:उत्तर|विकल्प|निष्कर्ष|कथन|आकलन)|应选|(?i:corresponde[ \t]+la[ \t]+opción))"
    r"[ \t]+\(?([A-D])" + _OPTION_END
)
_FINAL_ASSERTION = re.compile(
    _FINAL_START + r"\(?([A-D])\)?[ \t]+"
    r"(?i:(?:is[ \t]+(?:the[ \t]+)?(?:correct|best|compliant)"
    r"(?:[ \t]+(?:answer|option|choice|assessment|conclusion|response|proposition|account))?"
    r"|est[ \t]+la[ \t]+(?:(?:bonne|meilleure)[ \t]+réponse"
    r"|réponse[ \t]+(?:exacte|correcte))))"
    r"(?=[.。;!]|[ \t]*(?:$|\n))"
)
_FINAL_HEADING = re.compile(
    r"(?m)^[ \t]*(?:#{1,6}[ \t]+)?"
    r"(?i:final answer|최종[ \t]+답변|अंतिम[ \t]+निष्कर्ष|結論|答案)"
    r"[ \t]*[:：]?[ \t]*\n\s*\(?([A-D])" + _OPTION_END
)
_FINAL_BOX = re.compile(r"(?m)^[ \t]*\\boxed\{([A-D])\}[ \t]*[.。]?[ \t]*$")
_MULTI_CHOICE = re.compile(
    r"^\)?[.。।:：]?\s*(?:/|,|;|&|\+|(?i:or|and|ou|et|o|y|e|atau|dan)\b|或|和|及|、|또는|및|या|और)"
    r"\s*\(?[A-D](?=$|[\s).。।:：、,;!?/]|입니다|です)"
)


def extract_final_choice(prediction: str):
    """Extract a unique explicit conclusion from the final channel only."""
    from .output import final_answer_text

    final = final_answer_text(prediction).strip()
    if not final:
        return None, "empty_final_answer"
    # Formatting is not evidence of an answer, but must not hide a label or a
    # conflicting conclusion. Do not strip quote/list markers from prose.
    text = re.sub(r"^```(?:text|plaintext)?\s*", "", final, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]+(?=" + _FINAL_LABEL + r")", "", text).strip()
    choices = []
    ambiguous = False
    for pattern in (_FINAL_DECLARATION, _FINAL_DIRECT, _FINAL_ASSERTION,
                    _FINAL_HEADING, _FINAL_BOX):
        for match in pattern.finditer(text):
            choices.append(match.group(1))
            ambiguous |= bool(_MULTI_CHOICE.match(text[match.end():]))

    # A bare answer is allowed as the complete output or at its beginning with
    # an option delimiter. In particular, "A alternativa ..." and "A court ..."
    # are sentences, not bare option A. Explicit "A is correct" is also useful.
    bare = re.match(
        r"^\(?([A-D])(?=$|[).。।:：、,])", text
    )
    initial_letter = re.match(r"^\(?[A-D]", text)
    if initial_letter and _MULTI_CHOICE.match(text[initial_letter.end():]):
        ambiguous = True
    if bare:
        choices.append(bare.group(1))
        ambiguous |= bool(_MULTI_CHOICE.match(text[bare.end():]))
    # Also accept separate concluding letter lines, including after a label on
    # the preceding line. Different declared conclusions must never pick first
    # or last; a repeated identical conclusion remains unambiguous.
    for match in re.finditer(r"(?m)^[ \t]*\(?([A-D])\)?[.。।]?[ \t]*$", text):
        if not choices and match.start() != 0:
            continue
        choices.append(match.group(1))
        ambiguous |= bool(_MULTI_CHOICE.match(text[match.end():]))
    if ambiguous or len(set(choices)) > 1:
        return None, "ambiguous_final_choice"
    if not choices:
        return None, "no_anchored_final_choice"
    return choices[0], None
