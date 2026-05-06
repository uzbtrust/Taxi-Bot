# 🚕 Taxi Auto Bot

Telegram userbot orqali taxi guruhlariga avtomatik e'lon yuboradigan bot.

## Imkoniyatlar

- Telegram akkauntingizni ulab, userbot sifatida ishlatish
- Public (`@username`) va private (invite link) guruhlar qo'shish
- Bir vaqtda bir nechta kampaniya (habar) yuborish
- Yuborish intervalini tanlash: 1, 2, 3, 5, 15, 30, 60 daqiqa
- Har soatda eslatma — habar davom etsinmi yo to'xtatisinmi
- Statistika: yuborildi / xato soni
- O'zbek va Rus tili

## Texnologiyalar

- Python 3.11+
- aiogram 3.x — bot interfeysi
- Telethon — userbot (MTProto)
- SQLAlchemy 2.x async + aiosqlite
- APScheduler — interval scheduler
- Fernet — session shifrlash

## O'rnatish

```bash
git clone https://github.com/uzbtrust/Taxi-Bot.git
cd Taxi-Bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Sozlash

`.env` fayl yarating:

```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
FERNET_KEY=your_fernet_key
ADMIN_IDS=123456789
```

`FERNET_KEY` generatsiya qilish:

```bash
python gen_fernet_key.py
```

## Ishga tushirish

```bash
python main.py
```
