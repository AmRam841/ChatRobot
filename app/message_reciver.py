from Crypto.PublicKey import RSA

from Crypto.Cipher import PKCS1_OAEP
from  Crypto.Cipher import AES
from Crypto.IO import PKCS8
from Crypto.Random import get_random_bytes
from socket import *
from message_sender import Encrypted_data_package
import base64 , json
import socket



################################    key  loader    ################################
def load_private_key():
    with open("private_key.pem","r") as l :
        private_key = RSA.import_key(l.read())  
        return private_key
###################################################################################



################################    Decrypt The session key with RSA    ################################


    # encrypted_data_package RSA_encrypted_AES_key || NONCE || TAG || CIPHERTEXT

def rsa_decrypt(aes_key , private_key):
    
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_key = cipher.decrypt(aes_key)
    
    return decrypted_key
    
        



########################################################################################################


################################    Decrypt with AES    ################################
#RSA_encrypted_AES_key || NONCE || TAG || CIPHERTEXT
def decrypt_AES(decrypted_key , nonce , tag , ciphertext):
    cipehr_decrypt = AES.new(decrypted_key,AES.MODE_GCM, nonce=nonce)
    try :
        decrypted_data = cipehr_decrypt.decrypt_and_verify(ciphertext , tag)
        print("decrypted data : " , decrypted_data.decode())
        
    except:
        print("data fujed")
        
        
        
        
########################################################################################

################################    data unpacking     ################################

rsa_encryped_aes_key , nonce , tag , ciphertext = Encrypted_data_package

aes_key_decrypted = rsa_decrypt(rsa_encryped_aes_key , load_private_key())
data_decrypted_final = decrypt_AES(aes_key_decrypted , nonce , tag , ciphertext)




########################################################################################
################################    Data unserializer     ##############################






def deserialize_package(payload):
    d = json.loads(payload)
    return (
        base64.b64decode(d["rsa_encrypted_key"]),
        base64.b64decode(d["nonce"]),
        base64.b64decode(d["tag"]),
        base64.b64decode(d["ciphertext"])
    )
########################################################################################
    
    
        














