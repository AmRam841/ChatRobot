# this is a simple program to loook at time , availiblity andd doableity of this cause and why no one tried it 
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from rich.console import Console
#famous console line 
import os
console = Console()
#this was first designed as a file encryptor but now i want to make it into a message encryptor , i need to first clear my mind off these ideas . 1 - we create a mech that will encrypt the text with symetric key and then encrypt the key with rsa . 2- we do the same as 1 but we encrypt 
def encryption(intput_file,output_file,password):
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode('utf-8'),salt,dkLen=32 , count = 1000000)
    iv  =os.urandom(16)
    cypher = AES.new(key , AES.MODE_GCM , iv)


    try:
        with open(intput_file,'rb') as inputFile , open(output_file,'wb') as outputFile:
            outputFile.write(salt)
            outputFile.write(iv)
            
            while True:
                chunk = inputFile.read(4096)
                if len(chunk) == 0:
                    break
                if len(chunk) < 4096:
                    chunk = pad(chunk , 16)
                cypher_text = cypher.encrypt(chunk)
                outputFile.write(cypher_text)
                
                
    except FileNotFoundError:
        console.print("err file not found ")



def decryption(input_file,output_file,password):
    try:
        #read the enc file and read the first 32byte : 16 for salt , 16 for the IV
        with open(input_file ,'rb') as inputFile:
            salt = inputFile.read(16)
            if len(salt) != 16:
                raise ValueError("Invalid file : salt is incomplete or missing ")
            iv = inputFile.read(16)
            if len(iv) != 16:
                raise ValueError("iv incomplete")
            #Drive the 32 byte AES using PBKDF2 with the password and salt
            key = PBKDF2(password.encode('utf-8') , salt , dkLen=32 , count = 1000000)
            #initilize a AES chipher in cbc mode with the key and iv 
            AESchiper = AES.new(key , AES.MODE_CBC , iv)
            #Read the remaining data in chunks
            with open(output_file , 'wb') as output_file:
              while True:
                chunk = inputFile.read(4096)
                #end of the file    
                if len(chunk) ==  0 :
                       break
                #decrypt the chunk of file 
                decrypted_chunk = AESchiper.decrypt(chunk)
                #decrypt each chunk removing PKC7 padding from the final chunk
                if inputFile.tell() == os.path.getsize(input_file):
                    decrypted_chunk = unpad(decrypted_chunk,16)
                    
                output_file.write(decrypted_chunk)
                        
                        
    except FileNotFoundError:
        console.print("[bold red]File not found ![/bold red] ")
    except ValueError as e :
         console.print(f"[bold red]Decryption err {e} [/bold red]")
         raise SystemExit(1)
