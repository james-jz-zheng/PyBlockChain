from sign import sign, verify
import urllib2
import pickle
import os
from flask import Flask

NODES = ['127.0.0.0:5000',]
THIS_NODE = '127.0.0.0:5000'

gold_starter = ('hfkHJcqWOmWwPqAwEkA+aDnjKMC', 'g3fiI0vwnbW+znP-yS550P1LuuGW1u1f+RHZe05KrNNJC3fIXHmskRTsos+z9H3JRZJ8LB0qm6wZwkKbu6JfHbsDgTnTtLmc6aXfgV6FZAMAf-yox-7OA+hL01V2AjE6kfzLafena5UqP5dt3A8Z8Hn0zp3EpR2G8fSTLB5KlKZ_iaaaaaaacq0-p3njO0wQPEQlZ2cddcWJcY9hnSsI3SmZcDkknzOjFkWXKKKaIaeLPYsWOjRadqYsVEEohtvweILYlx3aPfvS4dy3xaAiUaEn-olBRScqxV0TMqn1vDT6n0F+QrcqwJHoGwrqYkeSCG9T5YkP8+LyHpSEKCDu-SN_i25y-s7xZ5EIAMYSesho9CJ-yhF_FB8aJNCgIzPJ52m3PjUiuceaExeJhgAF-Sh98D9HDkBu+XqUA0FX8k6v-jnhDuVwFZrE5JGaEzHgfevPFW75UbGAh6cBTPbcLmRu7NgHeXns470mSQdbU3q1XLvwgOaF0LxJw7CwgsZ2TAyxQuYjzqxFX7K-J5XQ05wN2xUwrT', 'bwqkxghHjZxYZNCO0Z8nkGBOxqMXu0dZZA-nj+Eu6cU')
first_owner  = ('dXX6xZQhUKU1YdR1wiDnAaxBLgW', 'e8-OOw3+h0fKiSxX7xt4fSOxNPRmiEMHsXLGWb2LNVTyIWhnJcN3qUJz-mhM7arISCdunscuikuqPKQrmX7xZ6D3akCEJTV0KBbFAJBQHlhRxirUo5yNx2d6EzJK1BqVRQmIj9DrhSsJJRlPkh5j5V5AryN89nvqKPqverVsboU_iaaaaaaaaahoimLwedRC2szxBbWOMEhTjyeRihBhbz+Vgsv+h3BJmKXrtAvwlCMwQxWxJiYpJww4QmgdVx-Ml1OykP8LpL5OlLn0nMSTV-bgex+pYD5-A8yfc6OyqAynnEHJGGk41K23Fukw3IPohbdJQcXkkxxqRMBg7f0kO41_pKeqyOjx3Lcosc9uezcMK68w7cd_dvjbFSzZewcacIfjfqVRHW+J5fxHjktVSXkQ5GIpT-ap5LlGoX20ztOwPtc7P3WzzU5ygpIl8+xKirBm3Hwmj9SJni631MZZ1EYF+0S9yU4ovnpCtGTIxGNgK6ZYzTSGDo28EaZN4WCPVYtWjrNTJMjEhIt6eDqqCyECNRJHZbB', 'cNORUgxMqg7Qq4W7eFmG2yd8z-QreZdMB2kAMrC7eNV')
second_owner = ('Z2FUYQ876fYa4qv2LT6DgrCIMA', 'dsDQLwQC8qIMGDD3CvhmEbeNOQ1tvYDKEUysn3zegWBRA4uv2GAf+Zh2fyxL1sSa2HRAh9GFc8UMtwUm+LqKaLRuUgPecxvFRcW-co9+MOUTPaiyxC9kuzSuqZGL6MXpwK8W-PF8l0UODsAjDp3SeFFqw6rt44GNNre1q4VIwdy_iaaaaaaaaazkcX8r8c19CKx5UfP+F-v++2j9BszjNtmZD-I+u6eeldu4fKwwRxWhGKV+dk4l3Rt7jEwdCKPYkIYRw3GaMr9v2ozGE+L0cXjGfFwqfLBNLGPvHvICtr4iqRtUhU23frpxMZx4em6SkctN3JaHVBKnDm075KujmBp_kt-DVT1bR0Sx7uhTci6W2hyUdk9_eiG9XyVxA8IkZVGlUIyBKpLNE3YqJ8XP1wc2NtvLsj4Qe1FPF6XCEhZ1RUj0RRsXC9sIzLU+UO9JRmrPaHdrp-BIiJatT8S5nanw1q6dWlZvzF4NDqQITzvTYLcY4MW2yloFUawvHT0z-aZTItTgTCeZWil2T1GgUcl50cJG5lp', 'nmGwT7zGOBtlXmGmOmj6dY23zvAd-315+cTaAfMHMKx')

first_owner_prik, first_owner_pubk, first_owner_pubkh = first_owner
second_owner_prik, second_owner_pubk, second_owner_pubkh = second_owner
gold_prik, gold_pubk, gold_pubkh = gold_starter

ADDRESS_DICT = {
    first_owner_pubkh : first_owner_pubk,
    second_owner_pubkh : second_owner_pubk,
    gold_pubkh : gold_pubk,
}

MEMORY = {}

app = Flask(__name__)


def chain_verify(input_data):
    data = input_data.split('$')
    paired_data = tuple(zip(data[::2], data[1::2]))

    value, serial_no = paired_data[0]
    for i in range(1, len(paired_data)):
        sub_data = data[:i*2+2]
        msg = '$'.join(sub_data[:-1])
        prev_owner_pubk = sub_data[-2]
        if i == 1:
            pubk = gold_pubkh
        else:
            pubk = prev_owner_pubk
        signature = sub_data[-1]
        if not verify(ADDRESS_DICT[pubk], msg, signature):
            return False
    return True

def pay_to(coin, next_pubk, owner_pubk, owner_prik):
    msg = '{}${}'.format(coin, next_pubk)
    return msg + '$' + sign(owner_prik, ADDRESS_DICT[owner_pubk], msg)

def update(coin_id, input_data):
    global MEMORY
    if not MEMORY.has_key(coin_id):
        MEMORY[coin_id] = input_data
        return
    old = MEMORY[coin_id]
    new = input_data

    min_len = min(len(old), len(new))
    if len(new) > len(old) and old[:min_len] == new[:min_len]:
        MEMORY[coin_id] = new

def save():
    global MEMORY
    dump_file = r'/tmp/{}'.format(THIS_NODE.replace(':',"."))
    pickle.dump(MEMORY, dump_file)

def load():
    global MEMORY
    dump_file = r'/tmp/{}'.format(THIS_NODE.replace(':',"."))
    if os.path.exists(dump_file):
        MEMORY = pickle.dump(dump_file)

def start_chain():
    load()

def init_coin():
    coins = ['1${}${}$'.format(sn, first_owner_pubkh) + sign(gold_prik, gold_pubk, '1${}${}'.format(sn, first_owner_pubkh)) for sn in range(10)]
    for c in coins:
        print c
        process(c)

def sync(node):
    global MEMORY
    for k, v in MEMORY.items():
        url = node + r'/input/' + v
        res = urllib2.urlopen(url)
        res.read()

@app.route('/')
def hello():
    return '<html><body>Welcome to JZZ Coin page!</body></html>'


@app.route('/input/<data>')
def process(data):
    global  MEMORY
    coin_id = '$'.join(data.split('$')[:2])
    if not chain_verify(data):
        update(coin_id, data)
    else:
        MEMORY[coin_id] = data
    return 'success'


@app.route('/query/<account>')
def query(account):
    global MEMORY
    try:
        balance = []
        for k,v in MEMORY.items():
            if str(v.split('$')[-2]) == str(account):
                balance .append(k)
        amount = sum([int(x.split('$')[0]) for x in balance])
        return amount
    except:
        return ''

@app.route('/coin/<coin_id>')
def coin(coin_id):
    global MEMORY
    return MEMORY[coin_id]

def main():
    start_chain()
    init_coin()
    app.run()

if __name__ == '__main__':
    main()
