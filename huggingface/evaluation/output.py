"""Select the final channel from a legacy serialized response."""

def final_answer_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("prediction must be a string")
    return text.rsplit("</think>", 1)[-1].strip() if "</think>" in text else text
