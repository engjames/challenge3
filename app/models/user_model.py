import datetime
import jwt
from app import app, conn,bcrypt

cur = conn.cursor()

class User:
    """
    Table schema
    """

    cur.execute('''CREATE TABLE IF NOT EXISTS users
            ( user_id SERIAL PRIMARY KEY    NOT NULL,
            firstname         VARCHAR(255)     NOT NULL,
            lastname          VARCHAR(255)     NOT NULL,
            email             VARCHAR(255)     NOT NULL,
            password          VARCHAR(255)     NOT NULL,
            isAdmin           VARCHAR(255)     NOT NULL,           
            registered_on     DATE     NOT NULL );''')

    def __init__(self, firstname, lastname, email, password, isAdmin):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')).decode('utf-8')
        self.isAdmin = isAdmin
        self.registered_on = str(datetime.datetime.now())

    def save(self):
        """
        Persist the user in the database
        :param user:
        :return:
        """
        cur = conn.cursor()
        sql = """
            INSERT INTO users (firstname, lastname, email, password, isAdmin, registered_on) 
                    VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql,(self.firstname, self.lastname, self.email, self.password, self.isAdmin, self.registered_on,))
        conn.commit()

    @staticmethod
    def get_by_email(user_email):
        """
        Filter a user by email.
        :param user_id:
        :return: user or None
        """
        cur = conn.cursor()
        sql1 = """
             SELECT * FROM users WHERE email=%s
        """
        cur.execute(sql1,(user_email,))
        user = cur.fetchone()
        return user

    @staticmethod
    def encode_auth_token(user_id):
        """
        Encode the Auth token
        :param user_id: User's Id
        :return:
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days = 1),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(token):
        """
        Decoding the token to get the payload and then return the user Id in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'],algorithms='HS256')
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            if is_token_blacklisted:
                return 'Token was Blacklisted, Please login In'
            return payload['sub']
        except jwt.ExpiredSignatureError:
             return 'Signature expired, Please sign in again'
        except jwt.InvalidTokenError:
             return 'Invalid key. Please sign in again'


class BlackListToken:
    """
    Table to store blacklisted/invalid auth tokens
    """
    cur.execute('''CREATE TABLE IF NOT EXISTS blacklist_token
        ( id SERIAL PRIMARY KEY    NOT NULL,
        token             VARCHAR(255)     NOT NULL,
        blacklisted_on     TIMESTAMP     NOT NULL );''')

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def blacklist(self):
        """
        Persist Blacklisted token in the database
        :return:
        """
        cur = conn.cursor()
        sql = """
            INSERT INTO blacklist_token (token,blacklisted_on) 
                    VALUES (%s,%s)
        """
        cur.execute(sql,(self.token,self.blacklisted_on,))
        conn.commit()

    @staticmethod
    def check_blacklist(token):
        """
        Check to find out whether a token has already been blacklisted.
        :param token: Authorization token
        :return:
        """
        cur = conn.cursor()
        sql1 = """
                SELECT token FROM blacklist_token WHERE token=%s
            """
        cur.execute(sql1,(token,))
        response = cur.fetchone()
        
        if response:
            return True
        return False
        
