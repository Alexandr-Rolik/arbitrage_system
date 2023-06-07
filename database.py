import pymysql as sql


class Database:

    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 3306
        self.user = "root"
        self.password = "root"
        self.database = "crypto_system"
        self.connection = None

    def connect(self):
        try:
            self.connection = sql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=sql.cursors.DictCursor
            )
            print("Succssfully connected to database...")
        except Exception as ex:
            print("Connetion to database refused...")
            print(ex)

    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
                print("Connection closed...")
            except Exception as ex:
                print("Failed to close connection...")
                print(ex)

    def check_login_exists(self, login):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user WHERE login = %s"
                cursor.execute(query, login)
                result = cursor.fetchone()
                if result:
                    return True
                else:
                    return False
        except Exception as ex:
            print("Login check error...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def insert_user(self, telegram_id, login, hashpass, contact_data):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO user (telegramId, login, hashpass, contactData) VALUES (%s, %s, %s, %s);"
                values = (telegram_id, login, hashpass, contact_data)
                cursor.execute(query, values)
                self.connection.commit()
                print("User ", login, " inserted successfully")
                return True
        except Exception as ex:
            print("Failed to insert user...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def find_user_by_login_db(self, login):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user WHERE login = %s"
                cursor.execute(query, login)
                self.connection.commit()
                user_data = cursor.fetchone()
                cursor.close()
                return user_data
        except Exception as ex:
            print("Failed to find user...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def find_user_by_telegram_id(self, telegram_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user WHERE telegramId = %s"
                cursor.execute(query, telegram_id)
                self.connection.commit()
                user_data = cursor.fetchone()
                cursor.close()
            if user_data:
                user_id = user_data['id']
                user_login = user_data['login']
                user_hashpass = user_data['hashpass']
                return user_id, user_login, user_hashpass
            else:
                return False
        except Exception as ex:
            print("Failed to find user...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_login_db(self, telegram_id, new_login):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user SET login = %s WHERE telegramId = %s"
                cursor.execute(query, (new_login, telegram_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change login...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_pass_db(self, telegram_id, new_hashpass):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user SET hashpass = %s WHERE telegramId = %s"
                cursor.execute(query, (new_hashpass, telegram_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change password...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_wallets_db(self, user_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user_wallet WHERE idUser = %s"
                cursor.execute(query, user_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def insert_wallet_db(self, user_id, name, address, private_key):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO user_wallet (idUser, name, address, privateKey) VALUES (%s, %s, %s, %s);"
                values = (user_id, name, address, private_key)
                cursor.execute(query, values)
                self.connection.commit()
                print("Wallet ", name, " inserted successfully")
                return True
        except Exception as ex:
            print("Failed to insert wallet...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_id_by_input_id(self, table_name, input_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT idUser FROM `{}` WHERE id = %s".format(table_name)
                cursor.execute(query, input_id)
                self.connection.commit()
                user_id = cursor.fetchone()
                cursor.close()
            if user_id:
                return user_id
            else:
                return False
        except Exception as ex:
            print("Failed to find user id from input id in table ", table_name, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_wallet_name_db(self, wallet_id, wallet_name):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_wallet SET name = %s WHERE id = %s"
                cursor.execute(query, (wallet_name, wallet_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change wallet name...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def delete_wallet_db(self, wallet_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM user_wallet WHERE id = %s"
                cursor.execute(query, wallet_id)
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to delete wallet ", wallet_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_exchanges_db(self, user_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user_exchange WHERE idUser = %s"
                cursor.execute(query, user_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user exchanges...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_exchange_account_data(self, account_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user_exchange WHERE id = %s"
                cursor.execute(query, account_id)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user exchange account...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_exchange_by_id(self, exchange_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM exchange WHERE id = %s"
                cursor.execute(query, exchange_id)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find exchange", exchange_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_exchange_by_name(self, exchange_name):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM exchange WHERE name = %s"
                cursor.execute(query, exchange_name)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find exchange ", exchange_name, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def add_user_exchange_account_db(self, user_id, exchange_id, account_name, public_key, secret_key):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO user_exchange (idUser, idExchange, accountName, publicKey, secretKey) VALUES (%s, %s, %s, %s, %s);"
                values = (user_id, exchange_id, account_name, public_key, secret_key)
                cursor.execute(query, values)
                self.connection.commit()
                print("Exchange account ", account_name, " inserted successfully")
                return True
        except Exception as ex:
            print("Failed to insert exchange account...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_user_exchange_account_name_db(self, user_exchange_id, account_name):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user_exchange SET accountName = %s WHERE id = %s"
                cursor.execute(query, (account_name, user_exchange_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change user exchange account name...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def delete_user_exchange_account_db(self, exchange_account_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM user_exchange WHERE id = %s"
                cursor.execute(query, exchange_account_id)
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to delete user exchange account ", exchange_account_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def insert_user_token(self, user_id, name, symbol, contract_address):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO crypto_asset (idUser, name, symbol, contractAddress) VALUES (%s, %s, %s, %s);"
                values = (user_id, name, symbol, contract_address)
                cursor.execute(query, values)
                self.connection.commit()
                new_token_id = cursor.lastrowid
                print("Token ", name, " inserted successfully")
                return new_token_id
        except Exception as ex:
            print("Failed to insert token...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def insert_trading_parameters(self, user_id, token_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO trading_parameters (idUser, idCrypto) VALUES (%s, %s);"
                values = (user_id, token_id)
                cursor.execute(query, values)
                self.connection.commit()
                print("Trading parameters for token ", token_id, " created successfully")
                return True
        except Exception as ex:
            print("Failed to create trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_tokens_db(self, user_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM crypto_asset WHERE idUser = %s"
                cursor.execute(query, user_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user tokens...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_token_data(self, token_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM crypto_asset WHERE id = %s"
                cursor.execute(query, token_id)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find token data...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def delete_token_db(self, token_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM crypto_asset WHERE id = %s"
                cursor.execute(query, token_id)
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to delete token ", token_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_trading_parameters_db(self, token_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM trading_parameters WHERE idCrypto = %s"
                cursor.execute(query, token_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def edit_trading_parameter_db(self, column_name, parameter_id, parameter_value):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = f"UPDATE trading_parameters SET {column_name} = %s WHERE id = %s"
                cursor.execute(query, (parameter_value, parameter_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to edit trading parameter...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_null_fields_of_trading_parameters(self, parameter_id, fields_string, where_condition):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                # Виконати запит для перевірки наявності полів зі значенням NULL за певним id
                query = f"SELECT {fields_string} FROM trading_parameters WHERE {where_condition}"
                cursor.execute(query, parameter_id)
                result = cursor.fetchone()
                if result:
                    # Знайдено принаймні одне поле зі значенням NULL за заданим id
                    return True
                else:
                    # Усі поля за заданим id мають значення, не рівне NULL
                    return False
        except Exception as ex:
            print("Failed to get null fields of trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_trading_wallet_db(self, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT idWallet FROM trading_parameters WHERE id = %s"
                cursor.execute(query, parameter_id)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user trading wallet...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_wallet_data(self, wallet_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user_wallet WHERE id = %s"
                cursor.execute(query, wallet_id)
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find data wallet ", {wallet_id}, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def connect_trading_wallet_db(self, wallet_id, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE trading_parameters SET idWallet = %s WHERE id = %s"
                cursor.execute(query, (wallet_id, parameter_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to set up wallet to trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def disconnect_trading_wallet_db(self, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE trading_parameters SET idWallet = NULL WHERE id = %s"
                cursor.execute(query, parameter_id)
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to disconnect wallet from trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_trading_accounts_db(self, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT idUserExchange FROM exchanges_trading_parameters WHERE idTradingParameters = %s"
                cursor.execute(query, parameter_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to check if exchange account already connected...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def check_exchange_account_already_connected(self, account_id, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM exchanges_trading_parameters WHERE idTradingParameters = %s AND idUserExchange = %s"
                cursor.execute(query, (parameter_id, account_id))
                self.connection.commit()
                result = cursor.fetchone()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to check if exchange account already connected...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def connect_exchange_account_db(self, account_id, parameter_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO exchanges_trading_parameters (idTradingParameters, idUserExchange) VALUES (%s, %s)"
                values = (parameter_id, account_id)
                cursor.execute(query, values)
                self.connection.commit()
                print("Exchange account ", account_id, " connected successfully to trading parameters")
                return True
        except Exception as ex:
            print("Failed to connect exchange account to trading parameters...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def disconnect_trading_exchange_account_db(self, parameter_id, account_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "DELETE FROM exchanges_trading_parameters WHERE idTradingParameters = %s AND idUserExchange = %s"
                cursor.execute(query, (parameter_id, account_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to disconnect user exchange account from trading parameters ", parameter_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_transactions_db(self, user_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM transaction WHERE idUser = %s"
                cursor.execute(query, user_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user transactions...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_requests_db(self, user_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM support_request WHERE idUser = %s"
                cursor.execute(query, user_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user support requests...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def create_support_request_db(self, user_id, user_chat_id, request_category, status, time_now):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO support_request (idUser, userChatId, category, status, dateCreated) VALUES (%s, %s, %s, %s, %s);"
                values = (user_id, user_chat_id, request_category, status, time_now)
                cursor.execute(query, values)
                self.connection.commit()
                new_request_id = cursor.lastrowid  # Отримання значення ID нового запиту
                print("Support request created successfully")
                return new_request_id
        except Exception as ex:
            print("Failed to create support request...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_request_by_id(self, request_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM support_request WHERE id = %s"
                cursor.execute(query, request_id)
                self.connection.commit()
                request_data = cursor.fetchone()
                cursor.close()
            if request_data:
                return request_data
            else:
                return False
        except Exception as ex:
            print("Failed to find request by id...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_user_request_messages_db(self, user_request_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM support_message WHERE idRequest = %s"
                cursor.execute(query, user_request_id)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to find user request messages...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def add_support_message_db(self, request_id, actor, content, time_now):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO support_message (idRequest, actor, content, date) VALUES (%s, %s, %s, %s);"
                values = (request_id, actor, content, time_now)
                cursor.execute(query, values)
                self.connection.commit()
                print("Support message added successfully")
                return True
        except Exception as ex:
            print("Failed to add support message...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def close_support_request_db(self, request_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE support_request SET status = 'closed' WHERE id = %s"
                cursor.execute(query, request_id)
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to close support request", request_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_users_list_db(self):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM user"
                cursor.execute(query)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to get list of users...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_user_role_db(self, user_id, new_role):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user SET role = %s WHERE id = %s"
                cursor.execute(query, (new_role, user_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change role for user", user_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_user_trading_status_db(self, user_id, new_status):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE user SET tradingStatus = %s WHERE id = %s"
                cursor.execute(query, (new_status, user_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change trading status for user", user_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_active_requests_db(self):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM support_request WHERE status='active'"
                cursor.execute(query)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to get list of active support requests...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def get_list_of_exchanges_db(self):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM exchange"
                cursor.execute(query)
                self.connection.commit()
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as ex:
            print("Failed to get list of exchanges...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def add_exchange_db(self, exchange_name, exchange_type):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "INSERT INTO exchange (name, type) VALUES (%s, %s);"
                values = (exchange_name, exchange_type)
                cursor.execute(query, values)
                self.connection.commit()
                print("Exchange added successfully")
                return True
        except Exception as ex:
            print("Failed to add exchange...")
            print(ex)
            return False
        finally:
            self.close_connection()

    def change_exchange_status_db(self, exchange_id, exchange_status):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                query = "UPDATE exchange SET status = %s WHERE id = %s"
                cursor.execute(query, (exchange_status, exchange_id))
                self.connection.commit()
                cursor.close()
                return True
        except Exception as ex:
            print("Failed to change status of exchange", exchange_id, "...")
            print(ex)
            return False
        finally:
            self.close_connection()


# if __name__ == '__main__':
#     db = Database()
#     db.connect()
#
#     # Додавання користувача до таблиці user
#     # db.insert_user("John", "john@example.com")
#
#     # Зчитування всіх користувачів з таблиці user
#     db.read_users()
#
#     # Закриття з'єднання з базою даних
#     db.close_connection()
