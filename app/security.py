from bcrypt import gensalt, hashpw, checkpw


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')

    return checkpw(password=password_byte_enc, hashed_password=hashed_password)


def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = gensalt()
    hashed_password = hashpw(password=pwd_bytes, salt=salt)
    string_hashed_password = hashed_password.decode('utf8')

    return string_hashed_password
