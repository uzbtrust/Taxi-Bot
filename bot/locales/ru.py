T = {
    "welcome": (
        "👋 Добро пожаловать в <b>Taxi Auto Bot</b>!\n\n"
        "Этот бот отправляет объявления в группы такси от вашего имени.\n\n"
        "Подключите аккаунт Telegram для начала."
    ),
    "welcome_back": "👋 Привет, <b>{name}</b>! Главное меню:",
    "connect_first": "⚠️ Сначала подключите аккаунт.",
    "auth_enter_phone": "📱 Введите номер телефона Telegram:\n<i>Пример: +998901234567</i>",
    "auth_invalid_phone": "❌ Неверный формат. Пример: <code>+998901234567</code>",
    "auth_sending_code": "⏳ Отправка кода...",
    "auth_enter_code": "📩 Код отправлен в Telegram.\nВведите код (с пробелами: <code>1 2 3 4 5</code>):",
    "auth_enter_2fa": "🔐 Введите ваш 2FA пароль:",
    "auth_wrong_code": "❌ Неверный код. Попробуйте ещё раз:",
    "auth_wrong_2fa": "❌ Неверный пароль. Попробуйте ещё раз:",
    "auth_success": "✅ Аккаунт успешно подключён!\n\n👤 <b>{name}</b> ({phone})",
    "auth_flood": "⏳ Telegram просит подождать {sec} секунд.",
    "auth_error": "❌ Ошибка: {error}\n\nДля повтора /start",
    "auth_already_exists": "⚠️ Этот номер уже подключён.",
    "main_menu": "🏠 <b>Главное меню</b>",
    "btn_accounts": "👤 Мои аккаунты",
    "btn_groups": "👥 Мои группы",
    "btn_broadcast": "📨 Отправить сообщение",
    "btn_settings": "⚙️ Настройки",
    "btn_help": "ℹ️ Помощь",
    "btn_back": "⬅️ Назад",
    "btn_cancel": "❌ Отмена",
    "accounts_empty": "👤 <b>Мои аккаунты</b>\n\nНет подключённых аккаунтов.",
    "accounts_list": "👤 <b>Мои аккаунты</b> ({count} шт):",
    "account_item": "{icon} <b>{name}</b> {phone}\n    📱 Групп: {groups}",
    "account_active": "✅",
    "account_paused": "⏸",
    "btn_add_account": "➕ Добавить аккаунт",
    "btn_toggle": "⏸ Пауза / ▶️ Продолжить",
    "btn_delete_account": "🗑 Удалить",
    "account_deleted": "🗑 Аккаунт удалён.",
    "account_toggled_on": "▶️ Аккаунт активирован.",
    "account_toggled_off": "⏸ Аккаунт на паузе.",
    "delete_confirm": "🗑 Удалить аккаунт <b>{name}</b>?\n\n⚠️ Все группы и кампании тоже удалятся!",
    "btn_confirm_delete": "✅ Да, удалить",
    "btn_no": "❌ Нет",
    "groups_empty": "👥 <b>Мои группы</b>\n\nГрупп нет. Добавьте через username или invite link.",
    "groups_list": "👥 <b>Мои группы</b> ({count}) | Стр {page}/{total}:",
    "group_item": "{icon} {title}",
    "group_active": "✅",
    "group_inactive": "🔴",
    "btn_add_group": "➕ Добавить группу",
    "btn_prev": "⬅️",
    "btn_next": "➡️",
    "groups_enter_input": (
        "📥 <b>Добавить группу</b>\n\n"
        "Отправьте:\n• <code>@username</code>\n• <code>https://t.me/+invite</code> (для private)\n"
    ),
    "group_resolving": "🔍 Проверяем группу...",
    "group_joining": "🔗 Вступаем в группу...",
    "group_added": "✅ Группа добавлена:\n<b>{title}</b>",
    "group_already_exists": "⚠️ Группа уже есть в списке.",
    "group_not_found": "❌ Группа не найдена или ссылка неверна.",
    "group_private_hint": "🔒 Группа приватная. Отправьте invite link: <code>https://t.me/+xxx</code>",
    "group_deleted": "🗑 Группа удалена.",
    "group_invalid_input": "❌ Неверный формат. Отправьте @username или invite link.",
    "group_join_error": "❌ Ошибка при вступлении: {error}",
    "select_account_for_groups": "👤 Для какого аккаунта смотреть группы?",
    "broadcast_no_groups": "⚠️ Групп нет! Сначала добавьте группы.",
    "broadcast_no_accounts": "⚠️ Нет активных аккаунтов.",
    "broadcast_menu": "📨 <b>Рассылка</b>\n\nДобавьте новое сообщение или просмотрите активные.",
    "btn_new_message": "➕ Новое сообщение",
    "btn_active_messages": "📋 Активные ({count} шт)",
    "broadcast_enter_message": "📝 <b>Рассылка</b>\n\nВведите текст сообщения:",
    "broadcast_active_exists": (
        "🔴 <b>Есть активная кампания!</b>\n\n"
        "📝 Текст: <code>{text}</code>\n"
        "⏱ Интервал: <b>{interval} мин</b>\n"
        "📊 Отправлено: <b>{sent}</b>\n"
        "👥 Групп: <b>{groups}</b>"
    ),
    "broadcast_preview": (
        "📋 <b>Подтверждение</b>\n\n"
        "📝 Сообщение:\n<code>{text}</code>\n\n"
        "👥 Групп: <b>{groups}</b>\n"
        "⏱ Интервал: <b>{interval} мин</b>\n"
        "👤 Аккаунт: <b>{account}</b>"
    ),
    "btn_start_broadcast": "🚀 Запустить",
    "broadcast_started": "🟢 <b>Кампания запущена!</b>\n\nКаждые <b>{interval}</b> мин → {groups} групп.",
    "broadcast_started_alert": "🟢 Кампания запущена! Каждые {interval} мин → {groups} групп.",
    "broadcast_paused": "⏸ Кампания на паузе.",
    "broadcast_resumed": "▶️ Кампания возобновлена.",
    "broadcast_stopped": "⏹ Кампания остановлена.",
    "broadcast_stats": (
        "📊 <b>Статистика кампании</b>\n\n"
        "📝 <code>{text}</code>\n"
        "⏱ Интервал: <b>{interval}</b> мин\n"
        "📤 Отправлено: <b>{sent}</b>\n"
        "👥 Групп: <b>{groups}</b>\n"
        "📅 Начало: <b>{started}</b>"
    ),
    "campaigns_empty": "📋 <b>Активные сообщения</b>\n\nАктивных нет.",
    "campaigns_list": "📋 <b>Активные сообщения</b> ({count} шт):",
    "campaign_detail": (
        "📊 <b>Сообщение {num}</b>\n\n"
        "📝 Текст: <code>{text}</code>\n"
        "⏱ Интервал: <b>{interval}</b> мин\n"
        "📤 Отправлено: <b>{sent}</b>\n"
        "❌ Ошибок: <b>{failed}</b>\n"
        "👥 Групп: <b>{groups}</b>\n"
        "📅 Начало: <b>{started}</b>"
    ),
    "btn_delete_campaign": "🗑 Остановить и удалить",
    "campaign_delete_confirm": "🗑 Остановить и удалить <b>сообщение {num}</b>?",
    "campaign_deleted": "⏹ Сообщение остановлено и удалено.",
    "reminder_text": (
        "⏰ <b>Это сообщение рассылается {hours} часов</b>\n\n"
        "📝 <code>{text}</code>\n\n"
        "Продолжать отправку?"
    ),
    "reminder_yes": "✅ Да, продолжать",
    "reminder_no": "❌ Остановить",
    "reminder_continued": "✅ Продолжаем!",
    "reminder_stopped": "⏹ Рассылка остановлена.",
    "btn_pause": "⏸ Пауза",
    "btn_resume": "▶️ Продолжить",
    "btn_stop": "⏹ Остановить",
    "btn_stats": "📊 Статистика",
    "select_interval": "⏱ <b>Выберите интервал</b> рассылки:",
    "select_account_for_broadcast": "👤 С какого аккаунта отправлять?",
    "settings_menu": "⚙️ <b>Настройки</b>\n\nТекущий язык: <b>{lang}</b>",
    "lang_changed": "✅ Язык изменён: <b>{lang}</b>",
    "help_text": (
        "ℹ️ <b>Taxi Auto Bot — Помощь</b>\n\n"
        "🔗 Подключите аккаунт Telegram\n"
        "👥 Добавьте группы такси\n"
        "📨 Введите текст и выберите интервал\n\n"
        "Бот будет отправлять сообщение от вашего имени."
    ),
    "notify_group_banned": "⚠️ Группа <b>{title}</b> заблокирована. Удалена из списка.",
    "notify_account_banned": "🚫 Аккаунт <b>{phone}</b> заблокирован. Кампания остановлена.",
    "notify_auto_stopped": "⏹ Кампания остановлена автоматически из-за ошибок.",
    "notify_sent_round": "📤 <b>Раунд завершён:</b> {ok} успешно, {fail} ошибок.",
    "error_generic": "❌ Произошла ошибка. Попробуйте снова.",
    "cancelled": "✅ Отменено.",
}
