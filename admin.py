import telebot
from telebot import types

from controller import Controller

controller = Controller()

bot = telebot.TeleBot("6217858884:AAExa_lNvKTBFltfHNAiTQ0OCEaub8FOk8Q")
# Зберігання інформації про авторизованих користувачів
authorized_users = set()


# Функція для перевірки авторизації користувача
def is_authorized(message):
    return message.from_user.id in authorized_users


def form_admin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    login_button = types.KeyboardButton('Логін')
    markup.add(login_button)
    bot.send_message(message.chat.id, "Вітаю! Оберіть опцію:", reply_markup=markup)


@bot.message_handler(commands=['start'])
def handle_start(message):
    form_admin(message)


@bot.message_handler(func=lambda message: message.text == 'Логін')
def login_step1(message):
    if is_authorized(message):
        bot.send_message(message.chat.id, "Ви вже авторизувалися.", reply_markup=main_menu_markup())
        return handle_menu(message)
    else:
        bot.send_message(message.chat.id, "Введіть логін:")
        bot.register_next_step_handler(message, login_step2)


def login_step2(message):
    login = message.text.lower()

    # Перевірка логіну на наявність неанглійських символів
    if not controller.check_input_validity(login):
        bot.send_message(message.chat.id, "Помилка! Логін повинен містити тільки англійські букви або цифри.")
        return form_admin(message)

    bot.send_message(message.chat.id, "Введіть пароль:")
    bot.register_next_step_handler(message, login_step3, login)


def login_step3(message, login):
    password = message.text.lower()

    # Перевірка пароля на наявність неанглійських символів
    if not controller.check_input_validity(password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
        return form_admin(message)

    telegram_id = message.from_user.id
    result = controller.find_user_by_login(login)

    if result:
        if controller.check_password(telegram_id, password):
            if result[2] == 'admin':
                bot.send_message(message.chat.id, "Ви успішно авторизовані!")
                authorized_users.add(telegram_id)
                return handle_menu(message)
            else:
                bot.send_message(message.chat.id,
                                 "Помилка! Ваш аккаунт не має адміністраторних прав.")
                return form_admin(message)
        else:
            bot.send_message(message.chat.id,
                             "Помилка! Невірний пароль aбо до Вашого telegram ID не прив'язаний жодний аккаунт.")
            return form_admin(message)
    else:
        bot.send_message(message.chat.id, "Помилка! Такого користувача не знайдено у системі.")
        return form_admin(message)


# Головне меню для адміна
def main_menu_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(telebot.types.KeyboardButton('Зареєструвати клієнта'),
               telebot.types.KeyboardButton('Список користувачів'),
               telebot.types.KeyboardButton('Список бірж'),
               telebot.types.KeyboardButton('Запити до служби підтримки'))
    return markup


@bot.message_handler(commands=['menu'])
def handle_menu(message):
    if is_authorized(message):
        bot.send_message(message.chat.id, "Вітаю Вас, оберіть команду з головного меню.",
                         reply_markup=main_menu_markup())
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_menu_messages(message):
    allowed_list = ['Зареєструвати клієнта', 'Список користувачів', 'Список бірж',
                    'Запити до служби підтримки']
    return message.text in allowed_list


# Обробка повідомлень з текстом
@bot.message_handler(func=allowed_menu_messages)
def handle_message_menu(message):
    text = message.text
    if is_authorized(message):
        if text == 'Зареєструвати клієнта':
            register_user(message)
        elif text == 'Список користувачів':
            list_of_users(message)
        elif text == 'Список бірж':
            list_of_exchanges(message)
        elif text == 'Запити до служби підтримки':
            list_of_requests(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def register_user(message):
    bot.send_message(message.chat.id, "Введіть telegram ID:")
    bot.register_next_step_handler(message, register_user_step2)


def register_user_step2(message):
    telegram_id = message.text.lower()

    if not telegram_id.isdigit():
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")
        return handle_menu(message)

    bot.send_message(message.chat.id, "Введіть логін:")
    bot.register_next_step_handler(message, register_user_step3, int(telegram_id))


def register_user_step3(message, telegram_id):
    login = message.text.lower()

    if not controller.check_input_validity(login):
        bot.send_message(message.chat.id, "Помилка! Логін повинен містити тільки англійські букви або цифри.")
        return handle_menu(message)

    bot.send_message(message.chat.id, "Введіть пароль:")
    bot.register_next_step_handler(message, register_user_step4, telegram_id, login)


def register_user_step4(message, telegram_id, login):
    password = message.text

    if not controller.check_input_validity(password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
        return handle_menu(message)

    bot.send_message(message.chat.id, "Введіть контактні дані:")
    bot.register_next_step_handler(message, register_user_step5, telegram_id, login, password)


def register_user_step5(message, telegram_id, login, password):
    contact_data = message.text

    if not controller.check_input_validity(contact_data):
        bot.send_message(message.chat.id,
                         "Помилка! Введене значення повинно містити тільки англійські букви або цифри.")
        return handle_menu(message)

    result = controller.process_registration(telegram_id, login, password, contact_data)

    bot.send_message(message.chat.id, result)
    return handle_menu(message)


def list_of_users(message):
    users_list = controller.get_users_list()
    if users_list:
        for user_data in users_list:
            user_id = user_data['user_id']
            response_message = f"\nID: {user_data['user_id']}\nTelegram ID: {user_data['user_telegram_id']}\n" \
                               f"Login: {user_data['user_login']}\nContact: {user_data['user_contact']}\n" \
                               f"Role: {user_data['user_role']}\nTrading status: {user_data['user_status']}\n"
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton("Змінити роль",
                                           callback_data=f"change_role_{user_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Змінити статус торгівлі",
                                           callback_data=f"change_trading_status_{user_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Переглянути історію торгів",
                                           callback_data=f"view_trading_history_{user_id}"))
            bot.send_message(message.chat.id, response_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Виникла помилка в отриманні списку користувачів.")


def process_callback_list_of_users(call, action, user_id):
    if action == 'change_role':
        bot.send_message(call.message.chat.id, "Введіть нову роль:")
        bot.register_next_step_handler(call.message, change_role_step1, user_id)
    elif action == 'change_trading_status':
        bot.send_message(call.message.chat.id, "Введіть статус торгівлі:")
        bot.register_next_step_handler(call.message, change_trading_status, user_id)
    elif action == 'view_trading_history':
        view_trading_history(call.message, user_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('change_role') or call.data.startswith(
        'change_trading_status') or call.data.startswith('view_trading_histor'))
def callback_handler_list_of_users(call):
    action, user_id = call.data.rsplit('_', maxsplit=1)
    process_callback_list_of_users(call, action, user_id)


def change_role_step1(message, user_id):
    new_role = message.text.lower()

    if not controller.check_input_validity(new_role):
        bot.send_message(message.chat.id,
                         "Помилка! Введене значення повинно містити тільки англійські букви або цифри.")
        return handle_menu(message)

    if new_role not in ['admin', 'client']:
        bot.send_message(message.chat.id, "Помилка! Ви ввели невалідне значення ролі.")
        return handle_menu(message)

    result = controller.change_user_role(user_id, new_role)
    bot.send_message(message.chat.id, result)


def change_trading_status(message, user_id):
    new_status = message.text.lower()

    if new_status not in ['active', 'inactive']:
        bot.send_message(message.chat.id, "Помилка! Ви ввели невалідне значення статусу.")
        return handle_menu(message)

    result = controller.change_user_traiding_status(user_id, new_status)
    bot.send_message(message.chat.id, result)


def view_trading_history(message, user_id):
    transactions_list = controller.get_user_transactions_list(user_id)
    if transactions_list:
        transaction_message = f"Торгові операції користувача {user_id}:\n"
        for transaction in transactions_list:
            transaction_message += f"\nID: {transaction['transaction_id']}\nКриптовалюта: {transaction['crypto_symbol']}\n" \
                                   f"Біржа купівлі: {transaction['buy_exchange_name']}\nАккаунт купівлі: {transaction['buy_exchange_account']}\n" \
                                   f"Біржа продажу: {transaction['sell_exchange_name']}\nАккаунт продажу: {transaction['sell_exchange_account']}\n" \
                                   f"Ціна купівлі: {transaction['price_buy']}\nЦіна продажу: {transaction['price_sell']}\n" \
                                   f"Кількість: {transaction['amount']}\nСтатус транзакції: {transaction['status']}\n" \
                                   f"Дата: {transaction['date']}"
        bot.send_message(message.chat.id, transaction_message)
    else:
        bot.send_message(message.chat.id, "У користувача немає жодної торгової операції.")


# Біржі додані до системи
def exchanges_list_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton('Підключити біржу'),
        telebot.types.KeyboardButton('Змінити статус біржі'),
    )
    return markup


def list_of_exchanges(message):
    if is_authorized(message):
        exchanges_list = controller.get_list_of_exchanges()
        if exchanges_list:
            exchanges = "Список бірж:\n"
            for exchange in exchanges_list:
                exchanges += f"\nID: {exchange['exchange_id']}, Біржа: {exchange['exchange_name']}, " \
                                    f"Тип: {exchange['exchange_type']}, Статус: {exchange['exchange_status']}\n"
            bot.send_message(message.chat.id, exchanges, reply_markup=exchanges_list_markup())
        else:
            bot.send_message(message.chat.id, "До системи не підключена жодна біржа.",
                             reply_markup=exchanges_list_markup())
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_exchagnes_list_messages(message):
    allowed_list = ['Підключити біржу', 'Змінити статус біржі']
    return message.text in allowed_list


@bot.message_handler(func=allowed_exchagnes_list_messages)
def handle_exchanges_list_choice(message):
    text = message.text

    if is_authorized(message):
        if text == 'Підключити біржу':
            add_exchange(message)
        elif text == 'Змінити статус біржі':
            edit_exchange(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def add_exchange(message):
    bot.send_message(message.chat.id, "Введіть назву біржі:")
    bot.register_next_step_handler(message, add_exchange_step2)


def add_exchange_step2(message):
    exchange_name = message.text.lower()

    if not controller.check_input_validity(exchange_name):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
        return handle_menu(message)

    bot.send_message(message.chat.id, "Введіть тип біржі:")
    bot.register_next_step_handler(message, add_exchange_step3, exchange_name)


def add_exchange_step3(message, exchange_name):
    exchange_type = message.text.lower()

    if not controller.check_input_validity(exchange_type):
        bot.send_message(message.chat.id, "Помилка! Тип повинен містити тільки англійські букви.")
        return handle_menu(message)

    result = controller.add_exchange(exchange_name, exchange_type)

    bot.send_message(message.chat.id, result)
    return handle_menu(message)


def edit_exchange(message):
    # Обробка натиснення кнопки "Видалити"
    bot.send_message(message.chat.id, "Введіть ID біржі:")
    bot.register_next_step_handler(message, edit_exchange_step2)


def edit_exchange_step2(message):
    exchange_id = message.text
    if not exchange_id.isdigit():
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")
        return handle_menu(message)

    bot.send_message(message.chat.id, "Введіть новий статус біржі:")
    bot.register_next_step_handler(message, edit_exchange_step3, exchange_id)


def edit_exchange_step3(message, exchange_id):
    exchange_status = message.text.lower()
    if exchange_status not in ['active', 'inactive']:
        bot.send_message(message.chat.id, "Помилка! Ви ввели невалідне значення статусу.")
        return handle_menu(message)

    result = controller.change_exchange_status(exchange_id, exchange_status)

    bot.send_message(message.chat.id, result)
    return handle_menu(message)


# Усі активні запити до служби підтримки
def list_of_requests(message):
    requests_list = controller.get_active_requests()
    if requests_list:
        for request_data in requests_list:
            request_id = request_data['request_id']
            response_message = f"\nID: {request_data['request_id']}\nUser ID: {request_data['request_user_id']}\n" \
                               f"Category: {request_data['request_category']}\nStatus: {request_data['request_status']}\n" \
                               f"Date created: {request_data['request_date_created']}\n"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("Переглянути запит",
                                           callback_data=f"view_request_{request_id}"))
            bot.send_message(message.chat.id, response_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Немає активних запитів.")


def process_callback_list_of_requests(call, action, request_id):
    if action == 'view_request':
        view_request_messages(call.message, request_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('view_request'))
def callback_handler_list_of_requests(call):
    action, request_id = call.data.rsplit('_', maxsplit=1)
    process_callback_list_of_requests(call, action, request_id)


def view_request_messages(message, request_id):
    messages_list = controller.get_request_messages(request_id)
    if messages_list:
        requests_message = f"Перелік повідомлень запиту {request_id}\n"
        for message_data in messages_list:
            requests_message += f"\nАвтор повідомлення: {message_data['message_actor']}\nВміст: {message_data['message_content']}\n" \
                                f"Дата повідомлення: {message_data['message_date']}\n"

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Додати повідомлення до запиту",
                                       callback_data=f"add_request_message_{request_id}"))
        keyboard.add(
            types.InlineKeyboardButton("Закрити запит",
                                       callback_data=f"close_request_{request_id}"))
        bot.send_message(message.chat.id, requests_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Виникла помилка в отриманні повідомлень запиту.")


def process_callback_list_of_messages(call, action, request_id):
    if action == 'add_request_message':
        bot.send_message(call.message.chat.id, "Додайте повідомлення до запиту:")
        bot.register_next_step_handler(call.message, add_response, request_id)
    elif action == 'close_request':
        close_request(call.message, request_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('add_request_message') or call.data.startswith('close_request'))
def callback_handler_list_of_requests(call):
    action, request_id = call.data.rsplit('_', maxsplit=1)
    process_callback_list_of_messages(call, action, request_id)


def add_response(message, request_id):
    content = message.text
    result = controller.add_message_to_request(request_id, 'admin', content)
    bot.send_message(message.chat.id, result)


def close_request(message, request_id):
    result = controller.close_user_support_request(request_id)
    bot.send_message(message.chat.id, result)


bot.polling(none_stop=True)
