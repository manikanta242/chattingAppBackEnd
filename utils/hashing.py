from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated = "auto"
)

def hashPassword(password : str): 
    print("--------------------------hashing---------------------------------------------")
    return pwd_context.hash(password)

def verifyPassword(plain_password:str,hash_password:str):
    return pwd_context.verify(plain_password,hash_password)
    