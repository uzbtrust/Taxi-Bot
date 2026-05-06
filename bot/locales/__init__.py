from bot.locales.uz import T as UZ
from bot.locales.ru import T as RU

_LOCALES = {"uz": UZ, "ru": RU}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    locale = _LOCALES.get(lang, UZ)
    text = locale.get(key) or UZ.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text
