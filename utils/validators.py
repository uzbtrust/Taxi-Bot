import re


def clean_phone(raw: str) -> str:
    phone = re.sub(r"[\s\-\(\)]", "", raw.strip())
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone


def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+\d{7,15}$", phone))


def clean_code(raw: str) -> str:
    return re.sub(r"\s+", "", raw.strip())


def parse_group_input(text: str) -> tuple[str, str]:
    """
    Returns (kind, value):
      kind = "username" | "invite" | "unknown"
      value = cleaned string
    """
    text = text.strip()
    invite_patterns = [
        r"https?://t\.me/\+([A-Za-z0-9_-]+)",
        r"https?://t\.me/joinchat/([A-Za-z0-9_-]+)",
        r"t\.me/\+([A-Za-z0-9_-]+)",
    ]
    for pat in invite_patterns:
        m = re.search(pat, text)
        if m:
            return "invite", text

    if text.startswith("@"):
        return "username", text
    if re.match(r"^[A-Za-z0-9_]{5,}$", text):
        return "username", "@" + text

    return "unknown", text
