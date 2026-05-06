# Taxi Auto Bot — Loyiha Rejasi

## Maqsad
Telegram userbot orqali taxi e'lon guruhlariga foydalanuvchi nomidan avtomatik (interval bilan) habar yuboradigan tizim. Foydalanuvchi botga o'z Telegram akkauntini ulaydi, kerakli guruhlarni qo'shadi, habar matnini yuboradi va intervalni tanlaydi — bot belgilangan vaqt oralig'ida o'sha habarni hamma guruhlarga foydalanuvchi nomidan yuboradi.

Misol: `"Toshkentga 3 ta odam kerak"` → 5 daqiqada bir marta 20 ta taxi guruhiga avtomatik yuboriladi.

## Texnologiyalar
- **Python 3.11+** (venv ichida)
- **aiogram 3.x** — bot interfeysi (foydalanuvchi bilan muloqot)
- **Telethon** — userbot (foydalanuvchi akkauntini ulash, guruhlarga habar yuborish)
- **SQLAlchemy 2.x (async) + aiosqlite** — ma'lumotlar bazasi
- **APScheduler (AsyncIOScheduler)** — interval bo'yicha ishga tushirish
- **pydantic-settings** — konfiguratsiya / .env
- **cryptography (Fernet)** — Telethon string session ni shifrlab DB ga yozish

## Loyiha tuzilmasi
```
Taxi Auto Bot/
├── .venv/                      # virtual muhit (gitignore)
├── .env                        # maxfiy kalitlar (gitignore)
├── .env.example                # namuna
├── .gitignore
├── requirements.txt
├── CLAUDE.md                   # shu fayl
├── README.md
├── main.py                     # entry point
├── config.py                   # Settings (BOT_TOKEN, API_ID, API_HASH, FERNET_KEY, ADMIN_IDS, DB_URL)
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # /start, til tanlash, onboarding
│   │   ├── auth.py             # akkaunt ulash (phone → code → 2FA)
│   │   ├── menu.py             # asosiy menyu
│   │   ├── accounts.py         # "Akkauntlarim" bo'limi
│   │   ├── groups.py           # "Guruhlarim" bo'limi
│   │   ├── broadcast.py        # "Habar" bo'limi (rassilka)
│   │   └── settings.py         # Sozlamalar / til
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py
│   │   └── reply.py
│   ├── states/
│   │   └── fsm.py              # FSM holatlari
│   ├── middlewares/
│   │   ├── db.py               # session injection
│   │   └── i18n.py             # til
│   └── locales/
│       ├── uz.py
│       └── ru.py
├── userbot/
│   ├── __init__.py
│   ├── client_manager.py       # bir nechta TelegramClient lar dispetcheri
│   ├── auth_flow.py            # phone → send_code → sign_in (2FA)
│   ├── group_resolver.py       # username / invite link → chat_id, join
│   └── sender.py               # guruhlarga habar yuborish (flood-wait safe)
├── scheduler/
│   ├── __init__.py
│   ├── scheduler.py            # AsyncIOScheduler global instance
│   └── jobs.py                 # broadcast job
├── db/
│   ├── __init__.py
│   ├── base.py                 # async engine, sessionmaker
│   ├── models.py               # User, Account, Group, Campaign, Message, Log
│   └── crud.py                 # repository funksiyalar
├── utils/
│   ├── __init__.py
│   ├── crypto.py               # Fernet shifrlash (string session)
│   ├── logger.py               # structlog / loguru
│   └── validators.py           # phone, username, invite link validatorlar
└── tests/
    └── ...                     # keyinroq
```

## Ma'lumotlar bazasi (modeli)

**User** — bot foydalanuvchisi
- `id` (tg_user_id, PK)
- `username`
- `language` (uz/ru)
- `created_at`

**Account** — ulangan Telegram akkaunt (userbot)
- `id` (PK)
- `user_id` (FK → User)
- `phone`
- `tg_account_id` — Telethon `me.id`
- `tg_username`
- `session_encrypted` — Fernet bilan shifrlangan string session
- `is_active` (bool) — pauza/davom
- `created_at`

**Group** — userbot ulangan taxi guruhi
- `id` (PK)
- `account_id` (FK → Account)
- `chat_id` — Telegram chat id
- `title`
- `username` (nullable, private bo'lsa null)
- `invite_link` (nullable)
- `is_active`
- `added_at`

**Campaign** — bitta rassilka kampaniyasi
- `id` (PK)
- `account_id` (FK → Account)
- `message_text` — yuboriladigan matn (yoki media file_id)
- `media_file_id` (nullable) — rasm/video bo'lsa
- `interval_minutes` — 1, 2, 3, 5, 15, 30, 60
- `status` — `running` / `paused` / `stopped`
- `groups_snapshot` — JSON list of group ids (kampaniya boshlanganda)
- `next_run_at`
- `total_sent`
- `created_at`, `stopped_at`

**SendLog** — har bir yuborilgan habar logi (debugging / statistika)
- `id`, `campaign_id`, `group_id`, `status` (ok/flood/forbidden/error), `error`, `sent_at`

## Bot oqimi (User Flow)

### 1. Onboarding (akkaunt yo'q)
- `/start` → "Salom! Taxi Auto Bot ga xush kelibsiz. Boshlash uchun Telegram akkauntingizni ulang."
- ▶️ tugma: `🔗 Akkaunt ulash`
- FSM: `Auth.waiting_phone` → telefon kontakt yoki +998... matn → `send_code_request`
- FSM: `Auth.waiting_code` → kod (formatda `1 2 3 4 5` yoki `12345` — kod telegram tomonidan invalidate qilinmasligi uchun bo'sh joy bilan ko'rsatamiz)
- FSM: `Auth.waiting_2fa` (agar 2FA yoqilgan bo'lsa) → cloud parol
- Muvaffaqiyatli → string session shifrlanib DB ga yoziladi → asosiy menyu

### 2. Asosiy menyu
Inline klaviatura, 3 ta tugma:
```
┌─────────────────────────────┐
│  👤 Akkauntlarim            │
├─────────────────────────────┤
│  👥 Guruhlarim              │
├─────────────────────────────┤
│  📨 Habar yuborish          │
└─────────────────────────────┘
│  ⚙️ Sozlamalar  │  ℹ️ Yordam │
```

### 3. Akkauntlarim
- Ulangan akkauntlar ro'yxati: `+998 90 *** ** 12 (@username) — ✅ faol`
- Har bir qator ustiga bosilsa: `▶️ pauza / ▶️ davom etish`, `🗑 o'chirish`, `🔄 sessiyani yangilash`
- `+ Yangi akkaunt qo'shish` tugmasi → onboarding qayta

### 4. Guruhlarim
- Joriy faol akkaunt uchun guruhlar ro'yxati (chunked, 1 sahifa = 10 ta)
- `+ Guruh qo'shish` tugmasi → 2 variant:
  - **Username orqali** (`@taxi_toshkent`) — userbot `client.get_entity` qiladi, agar a'zo bo'lmasa `JoinChannelRequest` orqali qo'shiladi
  - **Invite link orqali** (`https://t.me/+abc...` yoki `https://t.me/joinchat/...`) — `ImportChatInviteRequest` (private guruhlar uchun yagona to'g'ri yo'l)
  - **(Bonus)** Forward qilingan habar — agar userbot allaqachon a'zo bo'lsa, forward qilingan postdan chat ni aniqlaymiz
- Har bir guruh ustiga bosilsa: `🗑 o'chirish` (DB dan, lekin userbot guruhdan chiqmaydi — istasa qo'lda)
- `📥 Mening guruhlarimni import qilish` — userbot allaqachon a'zo bo'lgan barcha taxi-o'xshash guruhlarni topish (heuristic: title da "taxi", "yo'lovchi", "yo'lda" bor)

### 5. Habar yuborish
- ▶️ `📨 Habar yuborish` → "Yubormoqchi bo'lgan habarni yuboring (matn yoki rasm + caption)"
- FSM: `Broadcast.waiting_message` → user habarni yuboradi → bot saqlab oladi
- Bot intervalni so'raydi (inline):
  ```
  [ 1 daq ] [ 2 daq ] [ 3 daq ] [ 5 daq ]
  [ 15 daq ] [ 30 daq ] [ 60 daq ]
  [ ❌ Bekor qilish ]
  ```
- Tanlangach — preview va tasdiq:
  ```
  📨 Yuboriladigan habar:
  "Toshkentga 3 ta odam kerak..."

  📊 Guruhlar: 12 ta
  ⏱ Interval: 5 daqiqa
  👤 Akkaunt: +998 90 *** **12

  [✅ Boshlash]  [❌ Bekor]
  ```
- Tasdiqlangach — Campaign yaratiladi, APScheduler ga `interval` job qo'yiladi, birinchi yuborish darhol amalga oshiriladi.

### 6. Faol kampaniya boshqaruvi
- Habar yuborilayotganida menyuda yuqorida "🔴 Faol kampaniya: 5 daq, 12/15 ta yuborildi" kartochkasi turadi
- Tugmalar: `⏸ Pauza`, `▶️ Davom`, `⏹ To'xtatish`, `📊 Statistika`

## Userbot logikasi (Telethon)

### Sessiyani saqlash
- `StringSession()` ishlatamiz, login dan keyin `client.session.save()` → string → Fernet bilan shifrlab DB ga
- Foydalanishdan oldin DB dan o'qib, decrypt qilib `TelegramClient(StringSession(s), api_id, api_hash)` ni yaratamiz

### Bir nechta akkaunt — `client_manager.py`
- `dict[account_id, TelegramClient]` cache
- LRU style: 5 daqiqa ishlatilmasa `disconnect`
- `get_client(account_id)` — agar yo'q bo'lsa yaratadi, ulanadi, qaytaradi

### Habar yuborish (sender.py)
- Har bir guruhga `client.send_message(chat_id, text, file=...)`.
- **Flood wait** xatolari (`FloodWaitError`) — `asyncio.sleep(e.seconds)` qilib qayta urinmaydi (kampaniya intervaliga ishonamiz, log qilamiz)
- **Forbidden / Banned / Slowmode** — guruhni `is_active=False` qilib belgilab, foydalanuvchini xabardor qilamiz
- Guruhlar orasida 2-5 sekund tasodifiy uxlash (anti-spam)
- Har bir yuborish `SendLog` ga yoziladi

### Xavfsizlik / cheklovlar
- Akkaunt ban bo'lmasligi uchun **minimum interval 1 daqiqa** bo'lsa ham, agar guruhlar > 30 ta bo'lsa minimum 2 daqiqaga ko'chiramiz
- Bot bir vaqtda bir akkaunt uchun 1 ta faol kampaniya bilan cheklanadi (chalkashlikni oldini olish)

## Qo'shimcha featurelar (chiroyli qilish uchun)
1. **Statistika dashboard** — har kuni qancha habar yuborildi, qaysi guruh ko'p javob beradi (agar reply ni eshitsak)
2. **Habar shablonlari** — tez-tez ishlatadigan matnlarni saqlash (`Toshkent`, `Samarqand`, ...)
3. **Vaqt jadvali** — kampaniyani faqat ma'lum soatlarda ishga tushirish (masalan 06:00 – 23:00)
4. **Tasodifiy variatsiya** — bir xil matnga har safar oxiriga `🚗`, `🚕`, `✅` kabi emoji qo'shib bot detektsiyasidan qochish
5. **Preview mode** — birinchi yuborishni qilmasdan, "Mana bunday yuboriladi" deb test qilish
6. **Til** — uz/ru
7. **Admin paneli** — bot egasi uchun (loyiha egasi `ADMIN_IDS` da) — barcha userlarni ko'rish, bloklash, statistika
8. **Auto-stop** — agar 3 marta ketma-ket flood/banned bo'lsa, kampaniya avtomatik to'xtaydi va user xabardor qilinadi
9. **Limit (free vs premium)** — bepul: 1 akkaunt, 5 guruh, 5 daq min interval. (loyihaning monetizatsiya yo'lini ochiq qoldiramiz)

## Xavfsizlik
- `.env` da: `BOT_TOKEN`, `API_ID`, `API_HASH`, `FERNET_KEY` (`Fernet.generate_key()`), `ADMIN_IDS`, `DATABASE_URL`
- String session **hech qachon** plain saqlanmaydi
- Logarda telefon raqam va kodlar maskirovka qilinadi (`+99890***1234`)
- 2FA parol DB ga **umuman** saqlanmaydi — faqat sign-in paytida ishlatib tashlanadi

## O'rnatish va ishga tushurish
```bash
cd "/Users/uzbtrust/Desktop/Taxi Auto Bot"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env ni to'ldiring (BOT_TOKEN ni @BotFather dan, API_ID/API_HASH ni my.telegram.org dan)
python main.py
```

## Ishlash bosqichlari (sprintlar)
1. ✅ Skeleton + venv + requirements + .env.example + DB modelari + config
2. `/start` + onboarding (akkaunt ulash) — Auth FSM, Telethon login flow, session shifrlash
3. Asosiy menyu + Akkauntlarim bo'limi
4. Guruhlarim bo'limi (username + invite link)
5. Habar yuborish + APScheduler + sender
6. Kampaniya boshqaruvi (pauza / to'xtatish / statistika)
7. Qo'shimcha featurelar (shablonlar, vaqt jadvali, til, admin panel)
8. Test va deploy (VPS / systemd unit)

## Eslatmalar
- aiogram 3.x — `Router`, `F`, `Message`, `CallbackQuery`, `FSMContext` (storage `MemoryStorage` dev, `RedisStorage` prod)
- Telethon ni event loop ga aiogram bilan birga qo'shamiz (ikkalasi ham asyncio asosida) — `asyncio.gather(bot.start(), scheduler.start())`
- DB migratsiyalari: dastlabki versiyada `Base.metadata.create_all` yetarli; keyinroq Alembic
