from web3 import Web3
import ccxt
import requests


class Interaction:

    def __init__(self):
        self.provider_url = 'https://mainnet.infura.io/v3/086db83578d348ff9dd589bcfd40ca05'
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
        self.etherscan_api_key = 'WK1P54IXZCU7U7GPDNSJM7N7KMQT671G2T'

    def get_wallet_address(self, private_key):
        try:
            account = self.web3.eth.account.from_key(private_key)
            wallet_address = account.address
            return wallet_address
        except Exception as e:
            print(f"Помилка перевірки приватного ключа: {str(e)}")
            return False

    def get_balance(self, wallet_address):
        balance = self.web3.eth.get_balance(wallet_address)
        return self.web3.from_wei(balance, 'ether')

    @staticmethod
    def check_user_api_keys(exchange_name, public_key, secret_key):
        # Отримуємо клас біржі за допомогою функції getattr()
        exchange_class = getattr(ccxt, exchange_name.lower()) if hasattr(ccxt, exchange_name.lower()) else None

        if exchange_class is None:
            # Якщо немає підтримки для вказаної біржі, повертаємо помилку
            print(f"Помилка! Непідтримувана біржа: {exchange_name}")
            return False
        # Створюємо об'єкт біржі з використанням отриманого класу
        exchange = exchange_class({
            'apiKey': public_key,
            'secret': secret_key
        })
        try:
            # Виконуємо тестовий запит для перевірки ключів
            exchange.fetch_balance()
            return True  # API ключі вірні
        except Exception as ex:
            print(ex)
            return False  # API ключі невірні

    def get_token_info(self, contract_address):
        url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={self.etherscan_api_key}'
        checksum_address = self.web3.to_checksum_address(contract_address)
        try:
            response = requests.get(url)
            data = response.json()
            abi = data['result']
            # Створення екземпляра контракту
            contract = self.web3.eth.contract(address=checksum_address, abi=abi)
            # Отримання тикера монети
            ticker = contract.functions.symbol().call()
            # Отримання назви монети
            name = contract.functions.name().call()
            return name, ticker

        except Exception as ex:
            print(ex)
            return False

    @staticmethod
    def check_exchange_connection(exchange_name):
        exchange_class = getattr(ccxt, exchange_name.lower()) if hasattr(ccxt, exchange_name.lower()) else None

        if exchange_class is None:
            # Якщо немає підтримки для вказаної біржі, повертаємо помилку
            print(f"Помилка! Непідтримувана біржа: {exchange_name}")
            return False

        exchange = exchange_class()

        try:
            status = exchange.fetch_status()
            if status['status'] == 'ok':
                return True
            else:
                return False
        except ccxt.ExchangeError as e:
            print(f"Помилка підключення до біржі: {e}")

# if __name__ == '__main__':
#     inter = Interaction()
#     inter.check_infura_connection()
