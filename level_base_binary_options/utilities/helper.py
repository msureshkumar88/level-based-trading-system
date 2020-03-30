import hashlib

class Helper:
    @classmethod
    def password_encrypt(cls, password):
        h = hashlib.new('ripemd160')
        h.update(password.encode('utf-8'))
        return h.hexdigest()