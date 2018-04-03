### algo can be : DSA, ElGamal, DSA tested

import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.DSA as DSA
import Crypto.PublicKey.ElGamal as ElGamal
import Crypto.Util.number as CUN
import Crypto
import os
import pickle

# string.ascii_letters + string.digits + '-+'
CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+'
SEPERATOR = '_'
KEYBIT = 1024

ascd = dict(enumerate(CHARS))
ascdr = dict(map(reversed, ascd.items()))

def encode(n):
    bn, bl = bin(n)[2:], n.bit_length()
    nchars = int((bl + 5) / 6)
    n_extra0 = nchars * 6 - bl
    zeroed_n = '0'*n_extra0 + bn
    l = [ascd[eval('0b'+zeroed_n[i*6:(i+1)*6])] for i in range(nchars)]
    return ''.join(l)
    
def decode(s):
    return eval('0b'+''.join([('00000'+bin(ascdr[i])[2:])[-6:] for i in 'a'*((KEYBIT+5)/6-len(s))+s]))

def encode_all(l):
    return SEPERATOR.join([encode(i) for i in l])
    
def decode_all(s):
    return [decode(i) for i in s.split(SEPERATOR)]


# ypqgx
PRIVATE_KEY_FORMAT = "(iCrypto.PublicKey.DSA\n_DSAobj\np0\n(dp2\nS'y'\np3\nL{0}L\nsS'p'\np4\nL{1}L\nsS'q'\np5\nL{2}L\nsS'g'\np6\nL{3}L\nsS'x'\np7\nL{4}L\nsb."
PUBLIC_KEY_FORMAT  = "(iCrypto.PublicKey.DSA\n_DSAobj\np0\n(dp2\nS'y'\np3\nL{0}L\nsS'p'\np4\nL{1}L\nsS'q'\np5\nL{2}L\nsS'g'\np6\nL{3}L\nsb."
#pickle.dumps()
#pickle.loads(PRIVATE_KEY_FORMAT.format([ypqgx]))
#pickle.loads(PUBLIC_KEY_FORMAT.format([ypqg]))

def sign(private_key, public_key, message, algorithm=DSA):
    key_str = PRIVATE_KEY_FORMAT.format(*(decode_all(public_key) + [decode(private_key)]))
    private_key = pickle.loads(key_str)
    
    hash_code = SHA256.new(message).digest()
    if algorithm == DSA:
        K = CUN.getRandomNumber(128, os.urandom)
    elif algorithm == ElGamal:
        K = CUN.getPrime(128, os.urandom)
        while CUN.GCD(K, private_key.p - 1) != 1:
            print('K not relatively prime with {n}'.format(n=private_key.p - 1))
            K = CUN.getPrime(128, os.urandom)
    else:
        raise 'Error: only DSA/ElGamal are supported!'
    signature = private_key.sign(hash_code, K)
    return encode_all(signature)
    
def verify(public_key, message, signature, algorithm=DSA):
    public_key = pickle.loads(PUBLIC_KEY_FORMAT.format(*decode_all(public_key)))
    hash_code = SHA256.new(message).digest()
    return public_key.verify(hash_code, decode_all(signature))

def create_key(algorithm=DSA):
    private_key = algorithm.generate(KEYBIT, os.urandom)
    public_key = private_key.publickey()
    return key2string(private_key), key2string(public_key), hash_encode(public_key)

def key2string(key):
    k = key.key
    if key.has_private():
        return encode(k.x)
    else:
        return encode_all([k.y, k.p, k.q, k.g])
        
def string2key(key_str):
    ks = key_str.split(SEPERATOR)
    if len(ks) == 1:
        return decode(ks[0])
    else:
        return decode(key_str)

def hash_encode(public_key_str):
    return encode(eval('0x'+hash_key(public_key_str)))

def hash_key(key):
    return Crypto.Hash.SHA256.new(key2string(key)).hexdigest()


def main():
    message = 'JZZZZZ is a good developer!'

    private_key, public_key, _ = create_key()
    
    signature = sign(private_key, public_key, message)
    print('Verifying True msg:', verify(public_key, message, signature))
    print('public_key:', public_key)
    print('private_key:', private_key)
    print('signature:', signature)
    print('Verifying wrong msg:', verify(public_key, 'JZZZZZ is not a good developer!', signature))

if __name__ == "__main__":
    main()
