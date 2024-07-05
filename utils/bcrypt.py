import bcrypt



def hash_password(password: bytes) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password, salt=salt)


def compare_password(hashed_password: bytes, password: bytes) -> bool:
    return bcrypt.checkpw(password=password, hashed_password=hashed_password)