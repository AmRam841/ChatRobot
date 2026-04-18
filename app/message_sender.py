############################## imports ########################################
###############################################################################
from Crypto.PublicKey import RSA
import miniupnpc
from Crypto.Cipher import PKCS1_OAEP
from  Crypto.Cipher import AES
from Crypto.IO import PKCS8
from Crypto.Random import get_random_bytes
from socket import *

import json, base64


################################################################################
################################    find ip     ################################

def find_ip():
    """ Finds your public IP using  miniupnpc    
    """
    u = miniupnpc.UPnP()
    try:
    
     u.discover()
    
    except:
        pass
    
    try:
        u.selectigd()
        real_ip =   str(u.externalipaddress())
        return real_ip
    except:
        return u
###############################################################################

################################    Encrypt with AES    ################################
AES_session_key = get_random_bytes(32)

def AES_encrypt():
    #the AES should encrypt this and the rsa should encrypt the session keys 
    message = find_ip().encode("utf-8")
   # 256-bit key
    cipher = AES.new(AES_session_key, AES.MODE_GCM) # GCM generates its own nonce
# Encrypt
    data = message
    #RSA_encrypted_AES_key || NONCE || TAG || CIPHERTEXT
    nonce = cipher.nonce 
    tag,ciphertext = cipher.encrypt_and_digest(data)
    
    return nonce,tag,ciphertext
# To Decrypt (Receiver side)
# cipher_decrypt = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
# try:
#     decrypted_data = cipher_decrypt.decrypt_and_verify(ciphertext, tag)
#     print("Decrypted:", decrypted_data.decode())
# except ValueError:
#     print("WARNING: Data was tampered with!")

########################################################################################


################################    Load RSA Keys    ################################

def load_rsa_public_key():
    with open("public_key.pem" , "r") as f:
        public_key  = RSA.import_key(f.read())
        return public_key


# we can randomize the AES key !!!!!!!!!! if we have a bunch of text and we encrypt them with AES then we 

#################################################################################


################################    RSA Encryption     ################################

def rsa_encrypt(key , public_key):
    
    cipher = PKCS1_OAEP.new(public_key)
    
    return cipher.encrypt(key)

rsa_encrypted_key  = rsa_encrypt(AES_session_key, load_rsa_public_key())

#######################################################################################


################################    data     ################################
nonce,tag,ciphertext = AES_encrypt() 1
Encrypted_data_package = (rsa_encrypted_key , nonce , tag , ciphertext)
#############################################################################


################################ data serializer ################################
def Data_serializer(package):
    rsa_encrypted_key , nonce ,tag, ciphertext= package
    return json.dumps({
        "rsa_encrypted_key": base64.b64encode(rsa_encrypted_key).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    })
    


payload = Data_serializer(Encrypted_data_package)

with open("encrypted_msg.json", "w") as f:
    f.write(prepare_package_for_send(Encrypted_data_package))
