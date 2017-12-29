import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.DSA as DSA
import Crypto.PublicKey.ElGamal as ElGamal
import Crypto.Util.number as CUN
import Crypto
import os
import pickle
from binascii import hexlify, unhexlify
import string

ascd = dict(enumerate(string.ascii_letters + string.digits + '-+'))
ascdr = dict(map(reversed, ascd.items()))

def encode(n):
    bn, bl = bin(n)[2:], n.bit_length()
    nchars = (bl + 5) / 6
    n_extra0 = nchars * 6 - bl
    zeroed_n = '0'*n_extra0 + bn
    l = [ascd[eval('0b'+zeroed_n[i*6:(i+1)*6])] for i in range(nchars)]
    return ''.join(l)
    
def decode(s):
    return eval('0b'+''.join([('00000'+bin(ascdr[i])[2:])[-6:] for i in 'a'*(171-len(s))+s]))

encode_all = lambda l:'|'.join([encode(i) for i in l])
decode_all = lambda s:[decode(i) for i in s.split('|')]


# ypqgx
PRIVATE_KEY_FORMAT = "(iCrypto.PublicKey.DSA\n_DSAobj\np0\n(dp2\nS'y'\np3\nL{0}L\nsS'p'\np4\nL{1}L\nsS'q'\np5\nL{2}L\nsS'g'\np6\nL{3}L\nsS'x'\np7\nL{4}L\nsb."
PUBLIC_KEY_FORMAT  = "(iCrypto.PublicKey.DSA\n_DSAobj\np0\n(dp2\nS'y'\np3\nL{0}L\nsS'p'\np4\nL{1}L\nsS'q'\np5\nL{2}L\nsS'g'\np6\nL{3}L__________________\nsb."
#pickle.dumps()
#pickle.loads(PRIVATE_KEY_FORMAT.format([ypqgx]))
#pickle.loads(PUBLIC_KEY_FORMAT.format([ypqg]))


def sign(private_key, public_key, message, algorithm=DSA):
    
    private_key = pickle.loads(PRIVATE_KEY_FORMAT.format(decode_all(public_key) + [private_key]))
    
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
    return signature
    
def verify(public_key, message, signature, algorithm=DSA):
    public_key = pickle.loads(PUBLIC_KEY_FORMAT.format(decode_all(public_key)))
    hash_code = SHA256.new(message).digest()
    return public_key.verify(hash_code, signature)

def create_key(algorithm=DSA):
    private_key = algorithm.generate(1024, os.urandom)
    public_key = private_key.publickey()
    return key_tostring(private_key), key_tostring(public_key)

def key_tostring(key):
    k = key.key
    if key.has_private():
        print encode(k.x)
        return encode(k.x)
    else:
        print encode_all([k.y, k.p, k.q, k.g])
        return encode_all([k.y, k.p, k.q, k.g])
        
def string_tokey(key_str):
    ks = key_str.split('|')
    if len(ks) == 1:
        return decode(ks[0])
    else:
        return decode(key_str)


def hash_key(key):
    return Crypto.Hash.SHA256.new(key_tostring(key)).hexdigest()

# algo can be : DSA, ElGamal
algorithm = DSA
message = 'test message'

private_key, public_key = create_key()

signature = sign(private_key, public_key, message)
print verify(public_key, message, signature)
print 'private_key hex:', private_key
print 'signature:', signature
print 'public_key hex:', public_key

signature = sign(private_key, public_key, message+'a')
print verify(public_key, message, signature)
print 'private_key hex:', private_key
print 'signature:', signature
print 'public_key hex:', public_key
