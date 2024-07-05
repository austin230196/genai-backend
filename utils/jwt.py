import os

import jwt



def sign(session: dict) -> str:
    """
        Encodes this data into a jwt string
        @param {str} data: Data to be encoded
        @return {str}: JWT string
    """
    jwt_token = jwt.encode({"session": session}, os.getenv("SECRET_KEY"), algorithm="HS256")
    return jwt_token



def verify(token: str) -> any:
    """
        Verifies that a jwt session is still valid
    """
    try:
        payload = jwt.decode(token,  os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        return "JWT has already expired"