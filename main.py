import subprocess
import telebot
from telebot import types
from controller import Controller

# для запуску адмін бота
subprocess.Popen('python admin.py', shell=True)

controller = Controller()

bot = telebot.TeleBot("5946559668:AAF-duw9Wc3e7rS8dBFakKJPOltGiHZAK7o")
# Зберігання інформації про авторизованих користувачів
authorized_users = set()


# Функція для перевірки авторизації користувача
def is_authorized(message):
    return message.from_user.id in authorized_users


@bot.message_handler(commands=['start'])
def handle_start(message):
    form(message)


def form(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    login_button = types.KeyboardButton('Логін')
    register_button = types.KeyboardButton('Реєстрація')
    markup.add(login_button, register_button)

    bot.send_message(message.chat.id, "Вітаю! Оберіть опцію:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Реєстрація')
def register_step1(message):
    if is_authorized(message):
        bot.send_message(message.chat.id, "Ви вже авторизувалися.", reply_markup=main_menu_markup())
        return handle_menu(message)
    elif controller.get_user_login(message.from_user.id):
        bot.send_message(message.chat.id, "Помилка! За Вашим telegram ID вже є зареєстрований користувач.")
        return handle_start(message)
    else:
        bot.send_message(message.chat.id, "Введіть логін:")
        bot.register_next_step_handler(message, register_step2)


def register_step2(message):
    login = message.text.lower()

    if not controller.check_input_validity(login):
        bot.send_message(message.chat.id, "Помилка! Логін повинен містити тільки англійські букви або цифри.")
        return form(message)
    elif controller.check_login_exists(login):
        bot.send_message(message.chat.id, "Помилка! Логін зайнятий, спробуйте інший.")
    else:
        bot.send_message(message.chat.id, "Введіть пароль:")
        bot.register_next_step_handler(message, register_step3, login)


def register_step3(message, login):
    password = message.text
    telegram_id = message.from_user.id
    contact_data = message.from_user.username

    result = controller.process_registration(telegram_id, login, password, contact_data)

    bot.send_message(message.chat.id, result)
    return form(message)


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
        return form(message)

    bot.send_message(message.chat.id, "Введіть пароль:")
    bot.register_next_step_handler(message, login_step3, login)


def login_step3(message, login):
    password = message.text

    # Перевірка пароля на наявність неанглійських символів
    if not controller.check_input_validity(password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
        return form(message)

    telegram_id = message.from_user.id
    result = controller.find_user_by_login(login)

    if result:
        if controller.check_password(telegram_id, password):
            bot.send_message(message.chat.id, "Ви успішно авторизовані!")
            authorized_users.add(telegram_id)
            return handle_menu(message)
        else:
            bot.send_message(message.chat.id,
                             "Помилка! Невірний пароль aбо до Вашого telegram ID не прив'язаний жодний акаунт.")
            return form(message)
    else:
        bot.send_message(message.chat.id, "Помилка! Такого користувача не знайдено у системі.")
        return form(message)


# Головне меню
def main_menu_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(telebot.types.KeyboardButton('Налаштування профілю'),
               telebot.types.KeyboardButton('Додати криптовалюту'),
               telebot.types.KeyboardButton('Список криптовалют'),
               telebot.types.KeyboardButton('Історія торгівлі'),
               telebot.types.KeyboardButton('Запит до служби підтримки'))
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
    allowed_list = ['Налаштування профілю', 'Додати криптовалюту', 'Список криптовалют', 'Історія торгівлі',
                    'Запит до служби підтримки']  # Перелік дозволених повідомлень для головного меню
    return message.text in allowed_list


# Обробка повідомлень з текстом
@bot.message_handler(func=allowed_menu_messages)
def handle_message_menu(message):
    text = message.text
    if is_authorized(message):
        if text == 'Налаштування профілю':
            handle_profile_setting(message)
        elif text == 'Додати криптовалюту':
            add_token(message)
        elif text == 'Список криптовалют':
            view_user_tokens(message)
        elif text == 'Історія торгівлі':
            view_trading_history(message)
        elif text == 'Запит до служби підтримки':
            handle_support_request(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def profile_setting_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton('Зміна логіну'),
        telebot.types.KeyboardButton('Зміна паролю'),
        telebot.types.KeyboardButton('Налаштування акаунтів бірж'),
        telebot.types.KeyboardButton('Налаштування криптогаманця')
    )
    return markup


@bot.message_handler(commands=['profile'])
def handle_profile_setting(message):
    if is_authorized(message):
        login = controller.get_user_login(message.from_user.id)
        if login:
            bot.send_message(message.chat.id, f"Ваш логін {login}\nВиберіть пункт меню для налаштування.",
                             reply_markup=profile_setting_markup())
        else:
            bot.send_message(message.chat.id, "Помилка в отриманні логіну.")
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_profile_messages(message):
    allowed_list = ['Зміна логіну', 'Зміна паролю', 'Налаштування акаунтів бірж',
                    'Налаштування криптогаманця']  # Перелік дозволених повідомлень для профілю
    return message.text in allowed_list


@bot.message_handler(func=allowed_profile_messages)
def handle_profile_choice(message):
    # Обробка вибору пункту "Налаштування профілю"
    text = message.text

    if is_authorized(message):
        if text == 'Зміна логіну':
            change_login(message)
        elif text == 'Зміна паролю':
            change_pass(message)
        elif text == 'Налаштування акаунтів бірж':
            handle_user_exchange_setting(message)
        elif text == 'Налаштування криптогаманця':
            handle_wallet_setting(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def change_login(message):
    bot.send_message(message.chat.id, "Введіть новий логін:")
    bot.register_next_step_handler(message, check_login_availability)


def check_login_availability(message):
    login = message.text.lower()
    if not controller.check_input_validity(login):
        bot.send_message(message.chat.id, "Помилка! Логін повинен містити тільки англійські букви або цифри.")
    # Перевірка, чи зайнятий вже цей логін у системі
    elif controller.check_login_exists(login):
        bot.send_message(message.chat.id, "Помилка! Логін зайнятий, спробуйте інший.")
    else:
        bot.send_message(message.chat.id, "Введіть пароль для підтвердження:")
        bot.register_next_step_handler(message, confirm_password, login)


def confirm_password(message, new_login):
    password = message.text.lower()
    telegram_id = message.from_user.id

    if not controller.check_input_validity(password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
    elif controller.check_password(telegram_id, password):
        if controller.change_login(telegram_id, new_login):
            bot.send_message(message.chat.id, "Успішно змінено логін.")
            return handle_profile_setting(message)
        else:
            bot.send_message(message.chat.id, "Помилка у зміні логіну.")
    else:
        bot.send_message(message.chat.id, "Невірний пароль.")


def change_pass(message):
    bot.send_message(message.chat.id, "Введіть новий пароль:")
    bot.register_next_step_handler(message, confirm_new_password)


def confirm_new_password(message):
    new_password = message.text.lower()
    if not controller.check_input_validity(new_password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
    else:
        bot.send_message(message.chat.id, "Введіть поточний пароль для підтвердження:")
        bot.register_next_step_handler(message, check_current_password, new_password)


def check_current_password(message, new_password):
    current_password = message.text.lower()
    telegram_id = message.from_user.id

    if not controller.check_input_validity(current_password):
        bot.send_message(message.chat.id, "Помилка! Пароль повинен містити тільки англійські букви або цифри.")
    elif controller.check_password(telegram_id, current_password):
        if controller.change_password(telegram_id, new_password):
            bot.send_message(message.chat.id, "Успішно змінено пароль.")
            return handle_profile_setting(message)
        else:
            bot.send_message(message.chat.id, "Помилка у зміні паролю.")
    else:
        bot.send_message(message.chat.id, "Невірний поточний пароль.")


def wallet_setting_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        telebot.types.KeyboardButton('Підключити гаманець'),
        telebot.types.KeyboardButton('Редагувати гаманець'),
        telebot.types.KeyboardButton('Видалити гаманець'),
    )
    return markup


@bot.message_handler(commands=['wallet'])
def handle_wallet_setting(message):
    if is_authorized(message):
        user_id = controller.get_user_id(message.from_user.id)
        wallet_list = controller.get_user_wallets(user_id)
        if wallet_list:
            wallets_message = "Ваші підключені гаманці:\n"
            for wallet in wallet_list:
                wallets_message += f"ID: {wallet['wallet_id']}, Назва: {wallet['wallet_name']}, Адреса: {wallet['wallet_address']}\n"
            bot.send_message(message.chat.id, wallets_message, reply_markup=wallet_setting_markup())
        else:
            bot.send_message(message.chat.id, "Ви ще не маєте жодного підключеного гаманця.", reply_markup=wallet_setting_markup())
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_wallet_messages(message):
    allowed_list = ['Підключити гаманець', 'Редагувати гаманець',
                    'Видалити гаманець']  # Перелік дозволених повідомлень для налашутвання гаманця
    return message.text in allowed_list


@bot.message_handler(func=allowed_wallet_messages)
def handle_wallet_choice(message):
    text = message.text

    if is_authorized(message):
        if text == 'Підключити гаманець':
            add_wallet(message)
        elif text == 'Редагувати гаманець':
            edit_wallet(message)
        elif text == 'Видалити гаманець':
            delete_wallet(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def add_wallet(message):
    # Обробка натиснення кнопки "Підключити гаманець"
    bot.send_message(message.chat.id, "Введіть назву гаманця:")
    bot.register_next_step_handler(message, process_add_wallet_name)


def process_add_wallet_name(message):
    # Обробка введення назви гаманця
    wallet_name = message.text
    if not controller.check_input_validity(wallet_name):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
    else:
        bot.send_message(message.chat.id, "Введіть приватний ключ свого гаманця:")
        bot.register_next_step_handler(message, process_add_wallet_private_key, wallet_name)


def process_add_wallet_private_key(message, wallet_name):
    # Обробка введення приватного ключа гаманця
    private_key = message.text.lower()
    user_id = controller.get_user_id(message.from_user.id)
    if controller.validate_private_key(private_key):
        # Додати гаманець до бази даних
        if controller.add_wallet(user_id, wallet_name, private_key):
            bot.send_message(message.chat.id, "Гаманець успішно підключено.")
            handle_wallet_setting(message)  # Повернення до списку гаманців
        else:
            bot.send_message(message.chat.id, "Помилка! Підключення гаманця неуспішне.")
    else:
        bot.send_message(message.chat.id, "Помилка! Невалідний приватний ключ.")


def edit_wallet(message):
    # Обробка натиснення кнопки "Редагувати"
    bot.send_message(message.chat.id, "Введіть ID гаманця:")
    bot.register_next_step_handler(message, process_edit_wallet)


def process_edit_wallet(message):
    # Обробка введення ID гаманця
    wallet_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if wallet_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_wallet',
                                        wallet_id):  # Функція для перевірки валідності ID гаманця
            bot.send_message(message.chat.id, "Введіть нову назву гаманця:")
            bot.register_next_step_handler(message, process_edit_wallet_name, wallet_id)
        else:
            bot.send_message(message.chat.id, "Невірний ID гаманця. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def process_edit_wallet_name(message, wallet_id):
    # Обробка введення нової назви гаманця
    wallet_name = message.text
    if not controller.check_input_validity(wallet_name):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
    else:
        if controller.change_wallet_name(wallet_id, wallet_name):
            bot.send_message(message.chat.id, "Назву гаманця успішно змінено.")
            handle_wallet_setting(message)  # Повернення до списку гаманців
        else:
            bot.send_message(message.chat.id, "Помилка при зміні назви гаманця.")


def delete_wallet(message):
    # Обробка натиснення кнопки "Видалити"
    bot.send_message(message.chat.id, "Введіть ID гаманця:")
    bot.register_next_step_handler(message, process_delete_wallet_id)


def process_delete_wallet_id(message):
    # Обробка введення ID гаманця
    wallet_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if wallet_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_wallet',
                                        wallet_id):  # Функція для перевірки валідності ID гаманця
            if controller.delete_wallet(wallet_id):  # Функція для видалення гаманця з бази даних
                bot.send_message(message.chat.id, "Гаманець успішно видалено.")
                handle_wallet_setting(message)  # Повернення до списку гаманців
            else:
                bot.send_message(message.chat.id, "Помилка при видаленні гаманця.")
        else:
            bot.send_message(message.chat.id, "Невірний ID гаманця. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def user_exchange_setting_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        telebot.types.KeyboardButton('Підключити акаунт'),
        telebot.types.KeyboardButton('Редагувати акаунт'),
        telebot.types.KeyboardButton('Видалити акаунт'),
    )
    return markup


@bot.message_handler(commands=['exchange'])
def handle_user_exchange_setting(message):
    if is_authorized(message):
        user_id = controller.get_user_id(message.from_user.id)
        exchange_list = controller.get_user_exchanges(user_id)
        if exchange_list:
            exchange_message = "Ваші підключені акаунти:\n"
            for exchange in exchange_list:
                exchange_message += f"ID: {exchange['exchange_id']}, Біржа: {exchange['exchange_name']}, Акаунт: {exchange['account_name']}\n"
            bot.send_message(message.chat.id, exchange_message, reply_markup=user_exchange_setting_markup())
        else:
            bot.send_message(message.chat.id, "У вас немає підключених акаунтів.",
                             reply_markup=user_exchange_setting_markup())
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_user_exchange_messages(message):
    allowed_list = ['Підключити акаунт', 'Редагувати акаунт',
                    'Видалити акаунт']  # Перелік дозволених повідомлень для налашутвання підключення до біржі
    return message.text in allowed_list


@bot.message_handler(func=allowed_user_exchange_messages)
def handle_user_exchange_choice(message):
    text = message.text

    if is_authorized(message):
        if text == 'Підключити акаунт':
            add_user_exchange_account(message)
        elif text == 'Редагувати акаунт':
            edit_user_exchange_account(message)
        elif text == 'Видалити акаунт':
            delete_user_exchange_account(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def add_user_exchange_account(message):
    # Обробка натиснення кнопки "Додати акаунт"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Binance", callback_data='binance'))
    keyboard.add(types.InlineKeyboardButton("Bybit", callback_data='bybit'))
    bot.send_message(message.chat.id, "Виберіть біржу:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'binance')
def binance_handler(call):
    bot.send_message(call.message.chat.id, "Введіть назву акаунту: ")
    bot.register_next_step_handler(call.message, add_user_exchange_account_step2, call.data)


@bot.callback_query_handler(func=lambda call: call.data == 'bybit')
def bybit_handler(call):
    bot.send_message(call.message.chat.id, "Введіть назву акаунту: ")
    bot.register_next_step_handler(call.message, add_user_exchange_account_step2, call.data)


#
# @bot.callback_query_handler(func=lambda call: call.data == 'gate')
# def gate_handler(call):
#     bot.send_message(call.message.chat.id, "Введіть назву акаунту: ")
#     bot.register_next_step_handler(call.message, add_user_exchange_account_step2, call.data)


def add_user_exchange_account_step2(message, exchange_name):
    # Обробка введення назви акаунту
    account_name = message.text.lower()
    if not controller.check_input_validity(account_name):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
    else:
        bot.send_message(message.chat.id, "Введіть публічний API-ключ акаунту:")
        bot.register_next_step_handler(message, add_user_exchange_account_step3, exchange_name, account_name)


def add_user_exchange_account_step3(message, exchange_name, account_name):
    # Обробка введення публічного API-ключа акаунту
    public_key = message.text
    bot.send_message(message.chat.id, "Введіть секретний API-ключ акаунту:")
    bot.register_next_step_handler(message, add_user_exchange_account_step4, exchange_name, account_name, public_key)


def add_user_exchange_account_step4(message, exchange_name, account_name, public_key):
    # Обробка введення секретного API-ключа акаунту
    user_id = controller.get_user_id(message.from_user.id)
    secret_key = message.text
    if controller.is_user_api_valid(exchange_name, public_key,
                                    secret_key):  # Функція для перевірки валідності API-ключів
        if controller.add_user_exchange_account(user_id, exchange_name, account_name, public_key,
                                                secret_key):  # Функція для видалення гаманця з бази даних
            bot.send_message(message.chat.id, "Акаунт успішно підключено.")
            handle_user_exchange_setting(message)  # Повернення до списку акаунтів
        else:
            bot.send_message(message.chat.id, "Помилка! Підключення акаунту неуспішне.")
    else:
        bot.send_message(message.chat.id,
                         "Помилка при підключенні до акаунту. Перевірте правильність введених API-ключів.")


def edit_user_exchange_account(message):
    # Обробка натиснення кнопки "Редагувати"
    bot.send_message(message.chat.id, "Введіть ID акаунту:")
    bot.register_next_step_handler(message, process_edit_user_exchange_account)


def process_edit_user_exchange_account(message):
    # Обробка введення ID акаунту
    user_exchange_account_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if user_exchange_account_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_exchange',
                                        user_exchange_account_id):  # Функція для перевірки валідності ID акаунту користувача
            bot.send_message(message.chat.id, "Введіть нову назву акаунту:")
            bot.register_next_step_handler(message, process_edit_user_exchange_account_name, user_exchange_account_id)
        else:
            bot.send_message(message.chat.id, "Невірний ID акаунту. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def process_edit_user_exchange_account_name(message, user_exchange_account_id):
    # Обробка введення нової назви гаманця
    account_name = message.text
    if not controller.check_input_validity(account_name):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
    else:
        if controller.change_user_exchange_account_name(user_exchange_account_id, account_name):
            bot.send_message(message.chat.id, "Назву акаунту успішно змінено.")
            handle_user_exchange_setting(message)  # Повернення до списку акаунтів
        else:
            bot.send_message(message.chat.id, "Помилка при зміні назви акаунту.")


def delete_user_exchange_account(message):
    # Обробка натиснення кнопки "Видалити"
    bot.send_message(message.chat.id, "Введіть ID гаманця:")
    bot.register_next_step_handler(message, process_user_exchange_account)


def process_user_exchange_account(message):
    # Обробка введення ID гаманця
    exchange_account_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if exchange_account_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_exchange',
                                        exchange_account_id):  # Функція для перевірки валідності ID акаунту користувача
            if controller.delete_user_exchange_account(
                    exchange_account_id):  # Функція для видалення акаунту користувача з бази даних
                bot.send_message(message.chat.id, "Акаунт успішно видалено.")
                handle_user_exchange_setting(message)  # Повернення до списку акаунтів
            else:
                bot.send_message(message.chat.id, "Помилка при видаленні акаунту.")
        else:
            bot.send_message(message.chat.id, "Невірний ID акаунту. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


# Додати криптовалюту
def add_token(message):
    bot.send_message(message.chat.id, "Введіть адресу смарт-контракту криптовалюти:")
    bot.register_next_step_handler(message, process_add_token)


def process_add_token(message):
    contract_address = message.text
    telegram_id = message.from_user.id

    if not controller.check_input_validity(contract_address):
        bot.send_message(message.chat.id,
                         "Помилка! Адреса контракту повинна містити тільки англійські букви або цифри.")
    else:
        result = controller.add_user_token(telegram_id, contract_address)
        bot.send_message(message.chat.id, result)


def view_user_tokens(message):
    user_id = controller.get_user_id(message.from_user.id)

    token_list = controller.get_user_tokens(user_id)
    if token_list:
        first_message = f"Список доданих криптовалют:"
        bot.send_message(message.chat.id, first_message)

        for token_data in token_list:
            token_id = token_data['token_id']
            token_message = f"\nКриптовалюта: {token_data['token_name']}\nТикер: {token_data['token_symbol']}\n"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("Видалити криптовалюту",
                                           callback_data=f"delete_token_{token_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати параметри торгівлі",
                                           callback_data=f"edit_trading_parameters_{token_id}"))
            bot.send_message(message.chat.id, token_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "У Вас відсутні додані криптовалюти.")


def process_callback_data_token(call, action, token_id):
    if action == 'delete_token':
        delete_token(call.message, token_id)
    elif action == 'edit_trading_parameters':
        trading_parameters(call.message, token_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('delete_token') or call.data.startswith('edit_trading_parameters'))
def token_callback_handler(call):
    action, token_id = call.data.rsplit('_', maxsplit=1)
    process_callback_data_token(call, action, token_id)


def delete_token(message, token_id):
    result = controller.delete_user_token(token_id)
    bot.send_message(message.chat.id, result)


def trading_parameters(message, token_id):
    trading_parameters_list = controller.get_trading_parameters(token_id)

    if trading_parameters_list:
        first_message = f"Список торгових параметрів:"
        bot.send_message(message.chat.id, first_message)

        for parameter_data in trading_parameters_list:
            parameter_id = parameter_data['id']
            parameter_message = f"\nЧас опитування: {parameter_data['request_time']} сек.\nМінімальне значення спреду: {parameter_data['spread_min']}%\n" \
                                f"\nМінімальний об'єм купівлі: {parameter_data['amount_min']}$\nМаксимальний об'єм купівлі: {parameter_data['amount_max']}$\n" \
                                f"Мінімальний об'єм у стакані: {parameter_data['min_volume']}$\n\nСтатус торгівлі: {parameter_data['status']}\n"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати час опитування",
                                           callback_data=f"edit_request_time_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати значення спреду",
                                           callback_data=f"edit_spread_min_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати мінімальний об'єм купівлі",
                                           callback_data=f"edit_amount_min_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати максимальний об'єм купівлі",
                                           callback_data=f"edit_amount_max_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати мінімальний об'єм у стакані",
                                           callback_data=f"edit_min_volume_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Змінити статус торгівлі",
                                           callback_data=f"edit_status_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати доданий криптогаманець",
                                           callback_data=f"connected_wallet_{parameter_id}"))
            keyboard.add(
                types.InlineKeyboardButton("Налаштувати додані акаунти бірж",
                                           callback_data=f"connected_exchange_account_{parameter_id}"))
            bot.send_message(message.chat.id, parameter_message, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Помилка отримання торгових параметрів.")


def process_callback_trading_parameters(call, action, parameter_id):
    if action == 'edit_request_time':
        bot.send_message(call.message.chat.id, "Введіть цілочисельне значення часу опитування (у секундах):")
        bot.register_next_step_handler(call.message, edit_request_time, parameter_id)
    elif action == 'edit_spread_min':
        bot.send_message(call.message.chat.id, "Введіть цілочисельне значення мінімального спреду (у відсотках):")
        bot.register_next_step_handler(call.message, edit_spread_min, parameter_id)
    elif action == 'edit_amount_min':
        bot.send_message(call.message.chat.id, "Введіть цілочисельне значення мінімального об'єму купівлі:")
        bot.register_next_step_handler(call.message, edit_amount_min, parameter_id)
    elif action == 'edit_amount_max':
        bot.send_message(call.message.chat.id, "Введіть цілочисельне значення максимального об'єму купівлі:")
        bot.register_next_step_handler(call.message, edit_amount_max, parameter_id)
    elif action == 'edit_min_volume':
        bot.send_message(call.message.chat.id, "Введіть цілочисельне значення мінімального об'єму у стакані:")
        bot.register_next_step_handler(call.message, edit_min_volume, parameter_id)
    elif action == 'edit_status':
        bot.send_message(call.message.chat.id, "Введіть значення статусу (active або inactive) торгівлі:")
        bot.register_next_step_handler(call.message, edit_trading_status, parameter_id)
    elif action == 'connected_wallet':
        connected_wallet(call.message, parameter_id)
    elif action == 'connected_exchange_account':
        connected_exchange_account(call.message, parameter_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('edit_request_time') or call.data.startswith(
        'edit_spread_min') or call.data.startswith('edit_amount_min') or call.data.startswith(
        'edit_amount_max') or call.data.startswith('edit_min_volume') or call.data.startswith(
        'edit_status') or call.data.startswith('connected_wallet') or call.data.startswith(
        'connected_exchange_account'))
def trading_parameters_callback_handler(call):
    action, parameter_id = call.data.rsplit('_', maxsplit=1)
    process_callback_trading_parameters(call, action, parameter_id)


def edit_request_time(message, parameter_id):
    request_time = message.text

    if request_time.isdigit():
        request_time = int(request_time)
        if 2 <= request_time <= 3600:
            result = controller.edit_trading_parameter("requestTime", parameter_id, request_time)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id,
                             "Помилка! Введене значення повинно бути у діапазоні від 2 секунд до 3600 секунд.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def edit_spread_min(message, parameter_id):
    spread_min = message.text

    if spread_min.isdigit():
        spread_min = int(spread_min)
        if 1 <= spread_min <= 10000:
            spread_min = spread_min / 100
            result = controller.edit_trading_parameter("spreadMin", parameter_id, spread_min)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Помилка! Введене значення повинно бути у діапазоні від 1% до 10000%.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def edit_amount_min(message, parameter_id):
    amount_min = message.text

    if amount_min.isdigit():
        amount_min = int(amount_min)
        result = controller.edit_trading_parameter("amountMin", parameter_id, amount_min)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def edit_amount_max(message, parameter_id):
    amount_max = message.text

    if amount_max.isdigit():
        amount_max = int(amount_max)
        result = controller.edit_trading_parameter("amountMax", parameter_id, amount_max)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def edit_min_volume(message, parameter_id):
    min_volume = message.text

    if min_volume.isdigit():
        min_volume = int(min_volume)
        result = controller.edit_trading_parameter("minVolume", parameter_id, min_volume)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def edit_trading_status(message, parameter_id):
    new_status = message.text.lower()

    if new_status not in ['active', 'inactive']:
        bot.send_message(message.chat.id, "Помилка! Ви ввели невалідне значення статусу.")

    result = controller.edit_trading_status(parameter_id, new_status)
    bot.send_message(message.chat.id, result)


def connected_wallet(message, parameter_id):
    trading_wallet = controller.get_trading_wallet(parameter_id)
    if trading_wallet:
        wallet_message = "Доданий гаманець:"
        wallet_message += f"\nID: {trading_wallet['id']}\nНазва: {trading_wallet['name']}" \
                          f"\nАдреса: {trading_wallet['address']}\n"
        keyboard_1 = types.InlineKeyboardMarkup()
        keyboard_1.add(
            types.InlineKeyboardButton("Від'єднати гаманець",
                                       callback_data=f"disconnect_wallet_{parameter_id}"))
        bot.send_message(message.chat.id, wallet_message, reply_markup=keyboard_1)
    else:
        send_message = "До вибраної криптовалюти не доданий жодний гаманець."
        keyboard_2 = types.InlineKeyboardMarkup()
        keyboard_2.add(
            types.InlineKeyboardButton("Додати гаманець",
                                       callback_data=f"connect_wallet_{parameter_id}"))
        bot.send_message(message.chat.id, send_message, reply_markup=keyboard_2)


def process_callback_connected_wallet(call, action, parameter_id):
    if action == 'disconnect_wallet':
        disconnect_wallet(call.message, parameter_id)
    elif action == 'connect_wallet':
        bot.send_message(call.message.chat.id, "Введіть ID Вашого гаманця:")
        bot.register_next_step_handler(call.message, process_connect_wallet, parameter_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('disconnect_wallet') or call.data.startswith('connect_wallet'))
def connected_wallet_callback_handler(call):
    action, parameter_id = call.data.rsplit('_', maxsplit=1)
    process_callback_connected_wallet(call, action, parameter_id)


def disconnect_wallet(message, parameter_id):
    result = controller.disconnect_trading_wallet(parameter_id)
    bot.send_message(message.chat.id, result)


def process_connect_wallet(message, parameter_id):
    wallet_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if wallet_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_wallet', wallet_id):
            result = controller.connect_trading_wallet(wallet_id, parameter_id)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Невірний ID гаманця. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def connected_exchange_account(message, parameter_id):
    trading_exchange_accounts = controller.get_trading_trading_exchange_accounts(parameter_id)
    if trading_exchange_accounts:
        for account in trading_exchange_accounts:
            account_id = account['account_id']
            account_message = f"\nID: {account_id}\nБіржа: {account['exchange_name']}" \
                              f"\nАкаунт: {account['account_name']}\n"
            keyboard_1 = types.InlineKeyboardMarkup()
            keyboard_1.add(
                types.InlineKeyboardButton("Від'єднати акаунт біржі",
                                           callback_data=f"disconnect_exchange_account_{parameter_id}_{account_id}"))
            bot.send_message(message.chat.id, account_message, reply_markup=keyboard_1)

    send_message = "Для додавання акаунту натисніть кнопку:"
    keyboard_2 = types.InlineKeyboardMarkup()
    keyboard_2.add(
        types.InlineKeyboardButton("Додати акаунт біржі",
                                   callback_data=f"connect_exchange_account_{parameter_id}"))
    bot.send_message(message.chat.id, send_message, reply_markup=keyboard_2)


def process_callback_connected_exchange_account(call, action, parameter_id, account_id=None):
    if action == 'disconnect_exchange_account':
        disconnect_exchange_account(call.message, parameter_id, account_id)
    elif action == 'connect_exchange_account':
        bot.send_message(call.message.chat.id, "Введіть ID Вашого акаунту біржі:")
        bot.register_next_step_handler(call.message, process_connect_exchange_account, parameter_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('disconnect_exchange_account'))
def disconnected_account_callback_handler(call):
    action, parameter_id, account_id = call.data.rsplit('_', maxsplit=2)
    process_callback_connected_exchange_account(call, action, parameter_id, account_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('connect_exchange_account'))
def connected_account_callback_handler(call):
    action, parameter_id = call.data.rsplit('_', maxsplit=1)
    process_callback_connected_exchange_account(call, action, parameter_id)


def disconnect_exchange_account(message, parameter_id, account_id):
    result = controller.disconnect_trading_exchagne_account(parameter_id, account_id)
    bot.send_message(message.chat.id, result)


def process_connect_exchange_account(message, parameter_id):
    account_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if account_id.isdigit():
        if controller.is_valid_input_id(user_id, 'user_exchange', account_id):
            result = controller.connect_exchange_account(account_id, parameter_id)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Невірний ID акаунту. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def view_trading_history(message):
    user_id = controller.get_user_id(message.from_user.id)
    transactions_list = controller.get_user_transactions_list(user_id)
    if transactions_list:
        transaction_message = "Ваші торгові операції:\n"
        for transaction in transactions_list:
            transaction_message += f"\nID: {transaction['transaction_id']}\nКриптовалюта: {transaction['crypto_symbol']}\n" \
                                   f"Біржа купівлі: {transaction['buy_exchange_name']}\nАкаунт купівлі: {transaction['buy_exchange_account']}\n" \
                                   f"Біржа продажу: {transaction['sell_exchange_name']}\nАкаунт продажу: {transaction['sell_exchange_account']}\n" \
                                   f"Ціна купівлі: {transaction['price_buy']}\nЦіна продажу: {transaction['price_sell']}\n" \
                                   f"Кількість: {transaction['amount']}\nСтатус транзакції: {transaction['status']}\n" \
                                   f"Дата: {transaction['date']}"
        bot.send_message(message.chat.id, transaction_message)
    else:
        bot.send_message(message.chat.id, "У вас ще немає жодної торгової операції.")


# Запити до служби підтримки
def support_requests_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton('Створити запит'),
        telebot.types.KeyboardButton('Перегляд запиту'),
    )
    return markup


@bot.message_handler(commands=['support'])
def handle_support_request(message):
    if is_authorized(message):
        user_id = controller.get_user_id(message.from_user.id)
        requests_list = controller.get_user_requests_list(user_id)
        if requests_list:
            requests = "Ваші запити:\n"
            for request in requests_list:
                requests += f"\nID: {request['request_id']}, Категорія: {request['request_category']}, " \
                            f"Дата створення: {request['request_date']}, Статус: {request['request_status']}\n"
            bot.send_message(message.chat.id, requests, reply_markup=support_requests_markup())
        else:
            bot.send_message(message.chat.id, "У вас немає активних запитів.",
                             reply_markup=support_requests_markup())
    else:
        bot.send_message(message.chat.id,
                         "Помилка! Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def allowed_support_requests_messages(message):
    allowed_list = ['Створити запит',
                    'Перегляд запиту']  # Перелік дозволених повідомлень для запиту до служби підтримки
    return message.text in allowed_list


@bot.message_handler(func=allowed_support_requests_messages)
def handle_user_support_request_choice(message):
    text = message.text

    if is_authorized(message):
        if text == 'Створити запит':
            add_support_request(message)
        elif text == 'Перегляд запиту':
            view_support_request(message)
        else:
            bot.send_message(message.chat.id, "Невідома команда. Будь ласка, виберіть пункт з меню.")
    else:
        bot.send_message(message.chat.id,
                         "Вас не знайдено в списку авторизованих користувачів. Будь ласка, увійдіть у систему.")


def add_support_request(message):
    # Обробка натиснення кнопки "Додати запит"
    bot.send_message(message.chat.id, "Введіть назву категорії запиту:")
    bot.register_next_step_handler(message, add_support_request_step2)


def add_support_request_step2(message):
    # Обробка введення назви гаманця
    request_category = message.text
    if not controller.check_input_validity(request_category):
        bot.send_message(message.chat.id, "Помилка! Назва повинна містити тільки англійські букви або цифри.")
    else:
        bot.send_message(message.chat.id, "Введіть Ваше повідомлення:")
        bot.register_next_step_handler(message, add_support_request_step3, request_category)


def add_support_request_step3(message, request_category):
    # Обробка введення тексту повідомлення
    request_message = message.text
    user_id = controller.get_user_id(message.from_user.id)

    if controller.create_support_request(user_id, message.chat.id, request_category, request_message):
        bot.send_message(message.chat.id, "Ваш запит успішно створено. Очікуйте на відповідь адміністратора.")
        handle_support_request(message)  # Повернення до списку запитів
    else:
        bot.send_message(message.chat.id, "Помилка! Створення запиту неуспішне.")


def view_support_request(message):
    # Обробка натиснення кнопки "Перегляд запиту"
    bot.send_message(message.chat.id, "Введіть ID запиту:")
    bot.register_next_step_handler(message, process_view_support_request)


def process_view_support_request(message):
    # Обробка введення ID запиту
    user_request_id = message.text
    user_id = controller.get_user_id(message.from_user.id)
    if user_request_id.isdigit():
        if controller.is_valid_input_id(user_id, 'support_request', user_request_id):
            message_list = controller.get_request_messages(user_request_id)
            if message_list:
                requests_message = f"Перелік повідомлень запиту {user_request_id}\n"
                for message_data in message_list:
                    requests_message += f"\nАвтор повідомлення: {message_data['message_actor']}\nВміст: {message_data['message_content']}\n" \
                                        f"Дата повідомлення: {message_data['message_date']}\n"

                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton("Додати повідомлення до запиту",
                                               callback_data=f"add_request_message_{user_request_id}"))
                keyboard.add(
                    types.InlineKeyboardButton("Закрити запит",
                                               callback_data=f"close_request_{user_request_id}"))
                bot.send_message(message.chat.id, requests_message, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "Виникла помилка в отриманні повідомлень запиту.")
        else:
            bot.send_message(message.chat.id, "Невірний ID запиту. Спробуйте ще раз.")
    else:
        bot.send_message(message.chat.id, "Помилка! Введене значення не є числом.")


def process_callback_data(call, action, user_request_id):
    if action == 'add_request_message':
        bot.send_message(call.message.chat.id, "Додайте повідомлення до запиту:")
        bot.register_next_step_handler(call.message, add_support_request_message_step3, user_request_id)
    elif action == 'close_request':
        close_support_request(call.message, user_request_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('add_request_message') or call.data.startswith('close_request'))
def callback_handler(call):
    action, user_request_id = call.data.rsplit('_', maxsplit=1)
    process_callback_data(call, action, user_request_id)


def add_support_request_message_step3(message, user_request_id):
    # Обробка введення нової відповіді
    content = message.text
    result = controller.add_message_to_request(user_request_id, 'user', content)
    bot.send_message(message.chat.id, result)


def close_support_request(message, user_request_id):
    result = controller.close_user_support_request(user_request_id)
    bot.send_message(message.chat.id, result)


bot.polling(none_stop=True)

# if __name__ == '__main__':
#     main()
