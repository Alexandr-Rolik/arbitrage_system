import re
import telebot

from datetime import datetime
from argon2 import PasswordHasher
from cryptography.fernet import Fernet

from database import Database
from interaction import Interaction

db = Database()
inter = Interaction()
ph = PasswordHasher()
bot = telebot.TeleBot("5946559668:AAF-duw9Wc3e7rS8dBFakKJPOltGiHZAK7o")


class Controller:

    def __init__(self):
        self.fernet_path = 'key.txt'

    @staticmethod
    def hash_password(password):
        hashed_pass = ph.hash(password)
        if ph.check_needs_rehash(hashed_pass):
            return False
        else:
            return hashed_pass

    @staticmethod
    def verify_password(hashed_passwrod, password):
        try:
            return ph.verify(hashed_passwrod, password)
        except Exception as ex:
            print("Failed to check password")
            print(ex)
            return False

    def check_password(self, telegram_id, password):
        result = db.find_user_by_telegram_id(telegram_id)
        if result and self.verify_password(result[2], password):
            return True
        return False

    def read_encryption_key(self):
        with open(self.fernet_path, 'r') as file:
            # для того щоб отримати ключ у форматі bytes необхідно виконати .encode('utf-8')
            encryption_key = file.read().strip().encode('utf-8')
        return encryption_key

    def encrypt_data(self, data):
        encryption_key = self.read_encryption_key()
        cipher_suite = Fernet(encryption_key)
        # для того, щоб зашифрувати повідомлення str, його потрібно перевести у bytes за допомогою .encode('utf-8')
        cipher_text = cipher_suite.encrypt(data.encode('utf-8'))
        # переводимо закодоване повідомлення bytes назад у str за допомогою .decode('utf-8')
        encrypted_private_key = cipher_text.decode('utf-8')
        return encrypted_private_key

    def decrypt_data(self, encrypted_data):
        encryption_key = self.read_encryption_key
        cipher_suite = Fernet(encryption_key)
        # для того, щоб розшифрувати повідомлення str, його потрібно перевести у bytes за допомогою .encode('utf-8')
        decrypted_private_key = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
        # переводимо закодоване повідомлення bytes назад у str за допомогою .decode('utf-8')
        return decrypted_private_key.decode('utf-8')

    @staticmethod
    def check_input_validity(input_data):
        if re.match("^[a-zA-Z0-9]+$", input_data):
            return True
        else:
            return False

    @staticmethod
    def get_user_login(telegram_id):
        result = db.find_user_by_telegram_id(telegram_id)
        if result:
            user_login = result[1]
            return user_login
        else:
            return False

    @staticmethod
    def get_user_id(telegram_id):
        result = db.find_user_by_telegram_id(telegram_id)
        if result:
            user_id, user_login, user_hashpass = result
            return user_id
        else:
            return False

    def process_registration(self, telegram_id, login, password, contact_data):
        # Перевірка пароля на наявність неанглійських символів
        if not self.check_input_validity(password):
            return "Помилка! Пароль повинен містити тільки англійські букви або цифри."

        elif db.check_login_exists(login):
            return "Помилка! Користувач з таким логіном вже існує."

        hashed_password = self.hash_password(password)
        if db.insert_user(telegram_id, login, hashed_password, contact_data):
            return "Реєстрація успішна!"
        else:
            return "Помилка! Виникла помилка при реєстрації."

    @staticmethod
    def find_user_by_login(login):
        user_data = db.find_user_by_login_db(login)
        if user_data:
            telegram_id = user_data['telegramId']
            hashpass = user_data['hashpass']
            role = user_data['role']
            return telegram_id, hashpass, role
        else:
            return False

    @staticmethod
    def check_login_exists(login):
        return db.find_user_by_login_db(login)

    @staticmethod
    def change_login(telegram_id, new_login):
        if db.change_login_db(telegram_id, new_login):
            return True
        else:
            return False

    def change_password(self, telegram_id, new_password):
        hashpass = self.hash_password(new_password)
        if db.change_pass_db(telegram_id, hashpass):
            return True
        else:
            return False

    @staticmethod
    def get_user_wallets(user_id):
        result = db.get_user_wallets_db(user_id)
        wallets = []
        if result:
            for row in result:
                # Отримання даних гаманця та додавання їх до списку
                wallet_data = {
                    'wallet_id': row['id'],
                    'wallet_name': row['name'],
                    'wallet_address': row['address'],
                }
                wallets.append(wallet_data)
            return wallets
        else:
            return False

    @staticmethod
    def validate_private_key(private_key):
        if inter.get_wallet_address(private_key):
            return True
        else:
            return False

    def add_wallet(self, user_id, wallet_name, private_key):
        encrypted_private_key = self.encrypt_data(private_key)
        wallet_address = inter.get_wallet_address(private_key)

        return db.insert_wallet_db(user_id, wallet_name, wallet_address, encrypted_private_key)

    # перевірка, чи належить користувачу user введене значення id
    @staticmethod
    def is_valid_input_id(user_id, table_name, input_id):
        if table_name == 'user_wallet':
            wallet_id_user = db.get_user_id_by_input_id(table_name, input_id)
            if not wallet_id_user:
                return False
            return user_id == wallet_id_user['idUser']

        if table_name == 'user_exchange':
            exchange_account_id_user = db.get_user_id_by_input_id(table_name, input_id)
            if not exchange_account_id_user:
                return False
            return user_id == exchange_account_id_user['idUser']

        if table_name == 'support_request':
            support_request_id_user = db.get_user_id_by_input_id(table_name, input_id)
            if not support_request_id_user:
                return False
            return user_id == support_request_id_user['idUser']

    @staticmethod
    def change_wallet_name(wallet_id, wallet_name):
        if db.change_wallet_name_db(int(wallet_id), wallet_name):
            return True
        else:
            return False

    @staticmethod
    def delete_wallet(wallet_id):
        if db.delete_wallet_db(int(wallet_id)):
            return True
        else:
            return False

    @staticmethod
    def get_user_exchanges(user_id):
        result = db.get_user_exchanges_db(user_id)
        user_exchanges = []
        if result:
            for row in result:
                exchange_name = db.get_exchange_by_id(row['idExchange'])['name']

                # Отримання даних підключення та додавання їх до списку
                user_exchange_data = {
                    'exchange_id': row['id'],
                    'exchange_name': exchange_name,
                    'account_name': row['accountName'],
                }
                user_exchanges.append(user_exchange_data)
            return user_exchanges
        else:
            return False

    @staticmethod
    def is_user_api_valid(exchange_name, public_key, secret_key):
        return inter.check_user_api_keys(exchange_name, public_key, secret_key)

    def add_user_exchange_account(self, user_id, exchange_name, account_name, public_key, secret_key):
        encrypted_public_key = self.encrypt_data(public_key)
        encrypted_secret_key = self.encrypt_data(secret_key)
        exchange_id = db.get_exchange_by_name(exchange_name)['id']

        return db.add_user_exchange_account_db(user_id, exchange_id, account_name, encrypted_public_key,
                                               encrypted_secret_key)

    @staticmethod
    def change_user_exchange_account_name(user_exchange_id, account_name):
        if db.change_user_exchange_account_name_db(int(user_exchange_id), account_name):
            return True
        else:
            return False

    @staticmethod
    def delete_user_exchange_account(exchange_account_id):
        if db.delete_user_exchange_account_db(int(exchange_account_id)):
            return True
        else:
            return False

    def add_user_token(self, telegram_id, contract_address):
        user_id = self.get_user_id(telegram_id)
        token_info = inter.get_token_info(contract_address)
        if token_info:
            token_id = db.insert_user_token(user_id, token_info[0], token_info[1], contract_address)
            if db.insert_trading_parameters(user_id, token_id):
                return f"Криптовалюту {token_info[0], token_info[1]} успішно додано."
            else:
                return "Помилка! Виникла помилка при додаванні криптовалюти."
        else:
            return "Помилка! Введена адреса не є адресою смарт-контракту."

    @staticmethod
    def get_user_tokens(user_id):
        result = db.get_user_tokens_db(user_id)
        user_tokens = []
        if result:
            for row in result:
                user_token_data = {
                    'token_id': row['id'],
                    'token_name': row['name'],
                    'token_symbol': row['symbol'],
                }
                user_tokens.append(user_token_data)
            return user_tokens
        else:
            return False

    @staticmethod
    def delete_user_token(token_id):
        if db.delete_token_db(token_id):
            return "Криптовалюту успішно видалено."
        else:
            return "Виникла помилка при видаленні криптовалюти."

    @staticmethod
    def get_trading_parameters(token_id):
        result = db.get_trading_parameters_db(token_id)
        trading_parameters = []
        if result:
            for row in result:
                spread = row['spreadMin']
                trading_parameters_data = {
                    'id': row['id'],
                    'request_time': row['requestTime'],
                    'spread_min': spread,
                    'amount_min': row['amountMin'],
                    'amount_max': row['amountMax'],
                    'min_volume': row['minVolume'],
                    'status': row['status'],
                }
                trading_parameters.append(trading_parameters_data)
            return trading_parameters
        else:
            return False

    @staticmethod
    def edit_trading_parameter(column_name, parameter_id, parameter_value):
        if db.edit_trading_parameter_db(column_name, parameter_id, parameter_value):
            return "Параметр успішно налаштовано."
        else:
            return "Виникла помилка при налаштуванні параметру."

    @staticmethod
    def check_null_fields_of_trading_parameters(parameter_id):
        fields_to_check = ['idWallet', 'requestTime', 'spreadMin', 'amountMin', 'amountMax', 'minVolume']
        fields_string = ', '.join(fields_to_check)
        where_condition = f"id = %s AND ({' OR '.join(f'ISNULL({field})' for field in fields_to_check)})"
        return db.get_null_fields_of_trading_parameters(parameter_id, fields_string, where_condition)

    def edit_trading_status(self, parameter_id, new_status):
        # Для активації торгівлі необхідно, щоб кориcтувач підключив гаманець та хоча б один аккаунт біржі
        trading_accounts = db.get_trading_accounts_db(parameter_id)
        if not trading_accounts:
            return "Помилка! Неможливо активувати торгівлю, оскільки немає доданих аккаунтів біржі."

        # Перевірка наявності всіх налаштованих параметрів
        if self.check_null_fields_of_trading_parameters(parameter_id):
            return "Помилка! Неможливо активувати торгівлю, оскільки не всі параметри налаштовані."

        return self.edit_trading_parameter("status", parameter_id, new_status)

    @staticmethod
    def get_trading_wallet(parameter_id):
        wallet_id = db.get_trading_wallet_db(parameter_id)["idWallet"]
        if wallet_id:
            wallet_data = db.get_wallet_data(wallet_id)
            return wallet_data
        else:
            return False

    @staticmethod
    def connect_trading_wallet(wallet_id, parameter_id):
        if db.connect_trading_wallet_db(wallet_id, parameter_id):
            return "Гаманець успішно додано для торгівлі."
        else:
            return "Виникла помилка при додаванні гаманця."

    @staticmethod
    def disconnect_trading_wallet(parameter_id):
        if db.edit_trading_parameter_db('status', parameter_id, 'inactive') and db.disconnect_trading_wallet_db(
                parameter_id):
            return "Гаманець успішно від'єднано."
        else:
            return "Виникла помилка при від'єднанні гаманця."

    @staticmethod
    def get_trading_trading_exchange_accounts(parameter_id):
        trading_accounts = db.get_trading_accounts_db(parameter_id)
        if trading_accounts:
            user_connected_accounts = []

            for row in trading_accounts:
                account_id = row['idUserExchange']
                account_data = db.get_exchange_account_data(account_id)
                exchange_name = db.get_exchange_by_id(account_data['idExchange'])['name']

                user_exchange_data = {
                    'account_id': account_data['id'],
                    'exchange_name': exchange_name,
                    'account_name': account_data['accountName'],
                }
                user_connected_accounts.append(user_exchange_data)
            return user_connected_accounts
        return False

    @staticmethod
    def disconnect_trading_exchagne_account(parameter_id, account_id):
        if db.edit_trading_parameter_db('status', parameter_id,
                                        'inactive') and db.disconnect_trading_exchange_account_db(parameter_id,
                                                                                                  account_id):
            return "Аккаунт біржі успішно від'єднано."
        else:
            return "Виникла помилка при від'єднанні аккаунту біржі."

    @staticmethod
    def connect_exchange_account(account_id, parameter_id):
        if not db.check_exchange_account_already_connected(account_id, parameter_id):
            if db.connect_exchange_account_db(account_id, parameter_id):
                return "Аккаунт біржі успішно додано для торгівлі."
            else:
                return "Виникла помилка при додаванні аккаунту біржі."
        return "Даний аккаунт вже додано для торгівлі."

    @staticmethod
    def get_user_transactions_list(user_id):
        result = db.get_user_transactions_db(user_id)
        user_transactions = []
        if result:
            for row in result:
                crypto_id = row['idCryptoAsset']
                crypto_symbol = db.get_token_data(crypto_id)['symbol']

                buy_exchange_account_id = row['idBuyExchange']
                buy_account_data = db.get_exchange_account_data(buy_exchange_account_id)
                buy_exchange_name = db.get_exchange_by_id(buy_account_data['idExchange'])['name']

                sell_exchange_account_id = row['idSellExchange']
                sell_account_data = db.get_exchange_account_data(sell_exchange_account_id)
                sell_exchange_name = db.get_exchange_by_id(sell_account_data['idExchange'])['name']

                user_transaction_data = {
                    'transaction_id': row['id'],
                    'crypto_symbol': crypto_symbol,
                    'buy_exchange_name': buy_exchange_name,
                    'buy_exchange_account': buy_account_data['accountName'],
                    'sell_exchange_name': sell_exchange_name,
                    'sell_exchange_account': sell_account_data['accountName'],
                    'price_buy': row['priceBuy'],
                    'price_sell': row['priceSell'],
                    'amount': row['amount'],
                    'status': row['status'],
                    'date': row['date'],
                }
                user_transactions.append(user_transaction_data)
            return user_transactions
        else:
            return False

    @staticmethod
    def get_user_requests_list(user_id):
        result = db.get_user_requests_db(user_id)
        user_requests = []
        if result:
            for row in result:
                # Отримання даних підключення та додавання їх до списку
                user_exchange_data = {
                    'request_id': row['id'],
                    'request_category': row['category'],
                    'request_date': row['dateCreated'],
                    'request_status': row['status'],
                }
                user_requests.append(user_exchange_data)
            return user_requests
        else:
            return False

    @staticmethod
    def create_support_request(user_id, user_chat_id, request_category, request_message):
        time_now = datetime.now()
        new_request_id = db.create_support_request_db(user_id, user_chat_id, request_category, 'active', time_now)

        if new_request_id:
            time_now_2 = datetime.now()
            add_message_result = db.add_support_message_db(new_request_id, 'user', request_message, time_now_2)

            if add_message_result:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def get_user_chat_id(request_id):
        return db.get_request_by_id(request_id)['userChatId']

    @staticmethod
    def is_request_closed(request_id):
        request_status = db.get_request_by_id(request_id)['status']
        if request_status == 'closed':
            return True
        return False

    def add_message_to_request(self, request_id, actor, content):
        if self.is_request_closed(request_id):
            return "Помилка! Ви не можете додавати повідомлення до закритого запиту."
        time_now = datetime.now()
        add_message_result = db.add_support_message_db(request_id, actor, content, time_now)

        if add_message_result:
            if actor == 'admin':
                chat_id = self.get_user_chat_id(request_id)
                bot.send_message(chat_id, f"Aдміністратор додав відповідь на Ваш запит {request_id}.")
            return "Ваше повідомлення успішно додано."
        else:
            return "Помилка при додаванні повідомлення."

    def close_user_support_request(self, request_id):
        if self.is_request_closed(request_id):
            return "Помилка! Запит вже закритий."
        elif db.close_support_request_db(request_id):
            return "Запит успішно закрито."
        else:
            return "Помилка при закритті запиту."

    @staticmethod
    def get_request_messages(user_request_id):
        result = db.get_user_request_messages_db(user_request_id)
        request_messages = []
        if result:
            for row in result:
                # Отримання даних підключення та додавання їх до списку
                request_message_data = {
                    'message_actor': row['actor'],
                    'message_content': row['content'],
                    'message_date': row['date'],
                }
                request_messages.append(request_message_data)
            return request_messages
        else:
            return False

    @staticmethod
    def get_users_list():
        result = db.get_users_list_db()
        users_list = []
        if result:
            for row in result:
                request_message_data = {
                    'user_id': row['id'],
                    'user_telegram_id': row['telegramId'],
                    'user_login': row['login'],
                    'user_contact': row['contactData'],
                    'user_role': row['role'],
                    'user_status': row['tradingStatus'],
                }
                users_list.append(request_message_data)
            return users_list
        else:
            return False

    @staticmethod
    def change_user_role(user_id, new_role):
        if db.change_user_role_db(user_id, new_role):
            return "Роль успішно змінена."
        else:
            return "Помилка при зміні ролі."

    @staticmethod
    def change_user_traiding_status(user_id, new_status):
        if db.change_user_trading_status_db(user_id, new_status):
            return "Статус торгівлі успішно змінено."
        else:
            return "Помилка при зміні статуса торгівлі."

    @staticmethod
    def get_active_requests():
        result = db.get_active_requests_db()
        requests_list = []
        if result:
            for row in result:
                request_message_data = {
                    'request_id': row['id'],
                    'request_user_id': row['idUser'],
                    'request_category': row['category'],
                    'request_status': row['status'],
                    'request_date_created': row['dateCreated'],
                }
                requests_list.append(request_message_data)
            return requests_list
        else:
            return False

    @staticmethod
    def get_list_of_exchanges():
        result = db.get_list_of_exchanges_db()
        exchange_list = []
        if result:
            for row in result:
                request_message_data = {
                    'exchange_id': row['id'],
                    'exchange_name': row['name'],
                    'exchange_type': row['type'],
                    'exchange_status': row['status'],
                }
                exchange_list.append(request_message_data)
            return exchange_list
        else:
            return False

    @staticmethod
    def add_exchange(exchange_name, exchange_type):
        if not inter.check_exchange_connection(exchange_name):
            return "Помилка при підключенні до біржі."

        if db.add_exchange_db(exchange_name, exchange_type):
            return "Біржа успішно додана."
        else:
            return "Помилка при додаванні біржі."

    @staticmethod
    def change_exchange_status(exchange_id, exchange_status):
        if db.change_exchange_status_db(exchange_id, exchange_status):
            return "Статус біржі успішно змінено."
        else:
            return "Помилка при зміні статусу біржі."
