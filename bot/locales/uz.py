T = {
    # ── Start / Onboarding ─────────────────────────────────────────────────────
    "welcome": (
        "👋 <b>Taxi Auto Bot</b> ga xush kelibsiz!\n\n"
        "Bu bot taxi guruhlariga sizning akkauntingiz nomidan avtomatik e'lon yuboradi.\n\n"
        "Boshlash uchun Telegram akkauntingizni ulang."
    ),
    "welcome_back": "👋 Salom, <b>{name}</b>! Asosiy menyu:",
    "connect_first": "⚠️ Davom etish uchun avval akkaunt ulang.",

    # ── Auth ───────────────────────────────────────────────────────────────────
    "auth_enter_phone": (
        "📱 Telegram akkauntingiz telefon raqamini kiriting:\n"
        "<i>Misol: +998901234567</i>"
    ),
    "auth_invalid_phone": "❌ Noto'g'ri format. Misol: <code>+998901234567</code>",
    "auth_sending_code": "⏳ Telegram-dan kod yuborilmoqda...",
    "auth_enter_code": (
        "📩 <b>Kod yuborildi!</b>\n\n"
        "Kodni quyidagi joylardan birida qidiring:\n"
        "1️⃣ <b>Telegram ilovasi</b> → «Telegram» rasmiy akkauntidan xabar\n"
        "2️⃣ Agar Telegram o'rnatilmagan bo'lsa → SMS\n\n"
        "Kodni shu yerga yuboring (bo'sh joy bilan yozing):\n"
        "<code>1 2 3 4 5</code>"
    ),
    "auth_enter_2fa": "🔐 2FA parolingizni kiriting (cloud password):",
    "auth_wrong_code": "❌ Noto'g'ri kod. Qayta kiriting:",
    "auth_wrong_2fa": "❌ Parol noto'g'ri. Qayta kiriting:",
    "auth_success": "✅ Akkaunt muvaffaqiyatli ulandi!\n\n👤 <b>{name}</b> ({phone})",
    "auth_flood": "⏳ Telegram kutishni so'ramoqda. {sec} soniyadan keyin qayta urining.",
    "auth_error": "❌ Xatolik: {error}\n\nQayta urinish uchun /start",
    "auth_already_exists": "⚠️ Bu raqam allaqachon ulangan.",

    # ── Main menu ──────────────────────────────────────────────────────────────
    "main_menu": "🏠 <b>Asosiy menyu</b>",
    "btn_accounts": "👤 Akkauntlarim",
    "btn_groups": "👥 Guruhlarim",
    "btn_broadcast": "📨 Habar yuborish",
    "btn_settings": "⚙️ Sozlamalar",
    "btn_help": "ℹ️ Yordam",
    "btn_back": "⬅️ Orqaga",
    "btn_cancel": "❌ Bekor qilish",

    # ── Accounts ───────────────────────────────────────────────────────────────
    "accounts_empty": (
        "👤 <b>Akkauntlarim</b>\n\n"
        "Hech qanday akkaunt ulanmagan.\n"
        "Yangi akkaunt qo'shish uchun quyidagi tugmani bosing."
    ),
    "accounts_list": "👤 <b>Akkauntlarim</b> ({count} ta):",
    "account_item": "{icon} <b>{name}</b> {phone}\n    📱 Guruhlar: {groups} ta",
    "account_active": "✅",
    "account_paused": "⏸",
    "btn_add_account": "➕ Yangi akkaunt qo'shish",
    "btn_toggle": "⏸ Pauza / ▶️ Davom",
    "btn_delete_account": "🗑 O'chirish",
    "account_deleted": "🗑 Akkaunt o'chirildi.",
    "account_toggled_on": "▶️ Akkaunt faollashtirildi.",
    "account_toggled_off": "⏸ Akkaunt pauza qilindi.",
    "delete_confirm": "🗑 Haqiqatan ham <b>{name}</b> akkauntini o'chirmoqchimisiz?\n\n⚠️ Barcha guruhlar va kampaniyalar ham o'chadi!",
    "btn_confirm_delete": "✅ Ha, o'chir",
    "btn_no": "❌ Yo'q",

    # ── Groups ─────────────────────────────────────────────────────────────────
    "groups_empty": (
        "👥 <b>Guruhlarim</b>\n\n"
        "Hech qanday guruh qo'shilmagan.\n"
        "Guruh qo'shish uchun username yoki invite link yuboring."
    ),
    "groups_list": "👥 <b>Guruhlarim</b> ({count} ta) | Sahifa {page}/{total}:",
    "group_item": "{icon} {title}",
    "group_active": "✅",
    "group_inactive": "🔴",
    "btn_add_group": "➕ Guruh qo'shish",
    "btn_prev": "⬅️",
    "btn_next": "➡️",
    "groups_enter_input": (
        "📥 <b>Guruh qo'shish</b>\n\n"
        "Quyidagilardan birini yuboring:\n"
        "• <code>@guruh_username</code>\n"
        "• <code>https://t.me/+invite_link</code> (private guruhlar uchun)\n\n"
        "<i>Private guruhlar uchun guruh a'zosi invite linkini yuboring.</i>"
    ),
    "group_resolving": "🔍 Guruh tekshirilmoqda...",
    "group_joining": "🔗 Guruhga qo'shilmoqda...",
    "group_added": "✅ Guruh qo'shildi:\n<b>{title}</b>",
    "group_already_exists": "⚠️ Bu guruh allaqachon mavjud.",
    "group_not_found": "❌ Guruh topilmadi yoki link noto'g'ri.",
    "group_private_hint": "🔒 Bu guruh private. Invite link yuboring: <code>https://t.me/+xxx</code>",
    "group_deleted": "🗑 Guruh o'chirildi.",
    "group_invalid_input": "❌ Noto'g'ri format. Username (@group) yoki invite link yuboring.",
    "group_join_error": "❌ Guruhga qo'shilishda xatolik: {error}",
    "select_account_for_groups": "👤 Qaysi akkaunt uchun guruhlarni ko'rmoqchisiz?",

    # ── Broadcast ──────────────────────────────────────────────────────────────
    "broadcast_no_groups": (
        "⚠️ Guruhlar topilmadi!\n\n"
        "Avval <b>Guruhlarim</b> bo'limida guruh qo'shing."
    ),
    "broadcast_no_accounts": "⚠️ Faol akkaunt yo'q. Avval akkaunt ulang.",
    "broadcast_menu": (
        "📨 <b>Habar yuborish</b>\n\n"
        "Yangi habar qo'shing yoki aktiv habarlarni ko'ring."
    ),
    "btn_new_message": "➕ Yangi habar qo'shish",
    "btn_active_messages": "📋 Aktiv habarlar ({count} ta)",
    "broadcast_enter_message": (
        "📝 <b>Habar yuborish</b>\n\n"
        "Guruhlarga yuboriladigan habarni kiriting:\n"
        "<i>(faqat matn, max 4096 belgi)</i>"
    ),
    "broadcast_active_exists": (
        "🔴 <b>Faol kampaniya mavjud!</b>\n\n"
        "📝 Matn: <code>{text}</code>\n"
        "⏱ Interval: <b>{interval} daqiqa</b>\n"
        "📊 Yuborildi: <b>{sent}</b> ta\n"
        "👥 Guruhlar: <b>{groups}</b> ta"
    ),
    "broadcast_preview": (
        "📋 <b>Tasdiqlash</b>\n\n"
        "📝 Habar:\n<code>{text}</code>\n\n"
        "👥 Guruhlar: <b>{groups}</b> ta\n"
        "⏱ Interval: <b>{interval} daqiqa</b>\n"
        "👤 Akkaunt: <b>{account}</b>"
    ),
    "btn_start_broadcast": "🚀 Boshlash",
    "broadcast_started": (
        "🟢 <b>Kampaniya boshlandi!</b>\n\n"
        "⏱ Har <b>{interval}</b> daqiqada {groups} ta guruhga yuboriladi.\n"
        "Birinchi yuborish hoziroq amalga oshadi."
    ),
    "broadcast_started_alert": "🟢 Kampaniya boshlandi! Har {interval} daqiqada {groups} ta guruhga yuboriladi.",
    "broadcast_paused": "⏸ Kampaniya to'xtatildi (pauza).",
    "broadcast_resumed": "▶️ Kampaniya davom ettirildi.",
    "broadcast_stopped": "⏹ Kampaniya to'liq to'xtatildi.",
    "broadcast_stats": (
        "📊 <b>Kampaniya statistikasi</b>\n\n"
        "📝 Matn: <code>{text}</code>\n"
        "⏱ Interval: <b>{interval}</b> daqiqa\n"
        "📤 Jami yuborildi: <b>{sent}</b> ta\n"
        "👥 Guruhlar: <b>{groups}</b> ta\n"
        "📅 Boshlandi: <b>{started}</b>"
    ),
    "campaigns_empty": "📋 <b>Aktiv habarlar</b>\n\nHozircha faol habar yo'q.",
    "campaigns_list": "📋 <b>Aktiv habarlar</b> ({count} ta):",
    "campaign_detail": (
        "📊 <b>{num}-habar statistikasi</b>\n\n"
        "📝 Matn: <code>{text}</code>\n"
        "⏱ Interval: <b>{interval}</b> daqiqa\n"
        "📤 Yuborildi: <b>{sent}</b> ta\n"
        "❌ Xato: <b>{failed}</b> ta\n"
        "👥 Guruhlar: <b>{groups}</b> ta\n"
        "📅 Boshlandi: <b>{started}</b>"
    ),
    "btn_delete_campaign": "🗑 Habarni to'xtatish",
    "campaign_delete_confirm": "🗑 <b>{num}-habar</b>ni to'xtatib o'chirmoqchimisiz?",
    "campaign_deleted": "⏹ Habar to'xtatildi va o'chirildi.",
    "reminder_text": (
        "⏰ <b>Bu habar {hours} soatdan beri yuborilyabdi</b>\n\n"
        "📝 <code>{text}</code>\n\n"
        "Yuborilaversinmi?"
    ),
    "reminder_yes": "✅ Ha, davom etsin",
    "reminder_no": "❌ To'xtatish",
    "reminder_continued": "✅ Davom etadi!",
    "reminder_stopped": "⏹ Habar to'xtatildi.",
    "btn_pause": "⏸ Pauza",
    "btn_resume": "▶️ Davom",
    "btn_stop": "⏹ To'xtatish",
    "btn_stats": "📊 Statistika",
    "select_interval": "⏱ <b>Yuborish intervali</b>ni tanlang:",
    "select_account_for_broadcast": "👤 Qaysi akkauntdan yubormoqchisiz?",

    # ── Settings ───────────────────────────────────────────────────────────────
    "settings_menu": "⚙️ <b>Sozlamalar</b>\n\nJoriy til: <b>{lang}</b>",
    "lang_changed": "✅ Til o'zgartirildi: <b>{lang}</b>",

    # ── Help ───────────────────────────────────────────────────────────────────
    "help_text": (
        "ℹ️ <b>Taxi Auto Bot — Yordam</b>\n\n"
        "🔗 <b>Akkaunt ulash</b> — Telegram akkauntingizni ulab, userbot sifatida ishlatish\n"
        "👥 <b>Guruh qo'shish</b> — Public: @username, Private: invite link orqali\n"
        "📨 <b>Habar yuborish</b> — Matn kiriting → interval tanlang → kampaniya boshlanadi\n\n"
        "⚠️ <b>Eslatma:</b> Bot foydalanuvchi nomidan habar yuboradi. "
        "Guruh qoidalariga rioya qiling.\n\n"
        "🛡 Sessiya shifrlanib saqlanadi."
    ),

    # ── Notifications ─────────────────────────────────────────────────────────
    "notify_group_banned": (
        "⚠️ <b>Diqqat!</b>\n\n"
        "Guruh <b>{title}</b> ga yozish taqiqlandi yoki guruh o'chirildi.\n"
        "Guruh ro'yxatdan o'chirildi."
    ),
    "notify_account_banned": (
        "🚫 <b>Akkaunt bloklandi!</b>\n\n"
        "<b>{phone}</b> akkauntida xatolik yuz berdi. Kampaniya to'xtatildi.\n"
        "Akkauntni tekshiring."
    ),
    "notify_auto_stopped": (
        "⏹ <b>Kampaniya avtomatik to'xtatildi</b>\n\n"
        "Ketma-ket ko'p xatolik yuz berdi. Guruhlarni va akkauntni tekshiring."
    ),
    "notify_sent_round": "📤 <b>Yuborish tugadi:</b> {ok} ta muvaffaqiyatli, {fail} ta xatolik.",

    # ── Errors ─────────────────────────────────────────────────────────────────
    "error_generic": "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
    "cancelled": "✅ Bekor qilindi.",
}
