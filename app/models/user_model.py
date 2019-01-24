import datetime
import jwt
from app import app, conn, bcrypt

# establish a connection between our apllication and the database
cur = conn.cursor()


# User modal. this will be use as a template for creating objects of this class
class User:
    """
    Table schema
    """
    # lets create a users table if it doesnt exist
    cur.execute('''CREATE TABLE IF NOT EXISTS users
            ( user_id SERIAL PRIMARY KEY    NOT NULL,
            firstname         VARCHAR(255)     NOT NULL,
            lastname          VARCHAR(255)     NOT NULL,
            email             VARCHAR(255)     NOT NULL,
            password          VARCHAR(255)     NOT NULL,
            isAdmin           VARCHAR(255)     NOT NULL, registered_on \
            DATE NOT NULL );''')

    # this constructor is called each time we create a new user
    def __init__(self, firstname, lastname, email, password, isAdmin):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = bcrypt.generate_password_hash(password,
                                                      app.config.get(
                                                          'BCRYPT_LOG_ROUNDS'
                                                          )).decode('utf-8')
        self.isAdmin = isAdmin
        self.registered_on = str(datetime.datetime.now())

    # this saves users info into the database
    def save(self):
        """
        Persist the user in the database
        :param user:
        :return:
        """
        cur = conn.cursor()
        sql = """
            INSERT INTO users (firstname, lastname, email, password, isAdmin, \
            registered_on)
                    VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (self.firstname, self.lastname, self.email,
                    self.password, self.isAdmin, self.registered_on,))
        conn.commit()

    # statics methods donot require to first create an instance of a class t \
    # use them

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
        cur.execute(sql1, (user_email,))
        user = cur.fetchone()
        return user

    # This method is for generating a token
    @staticmethod
    def encode_auth_token(user_id):
        """
        Encode the Auth token
        :param user_id: User's Id
        :return:
        """
        # the token will contatins the data we want to encrypt, the expiration
        # date,
        # the key we're going to use to encrypt it, and the method we're to use
        # # sub refers to the data to be encrypted
        # secret key is the key we use to encrypt the data
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    # this method is used to decode our token
    @staticmethod
    def decode_auth_token(token):
        """
        Decoding the token to get the payload and then return \
        the user Id in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            # to decode the token, u need to pass the token to be decoded, the
            # key u used to encrypt it, and the method to use to decode it
            payload = jwt.decode(token, app.config['SECRET_KEY'],
                                 algorithms='HS256')

            # All tokens that have expired are stored in ablacklisted token
            # sothat they are not used again
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            # check if provided token to be decoded is among the blacklisted
            # ones
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
        cur.execute(sql, (self.token, self.blacklisted_on,))
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
        cur.execute(sql1, (token,))
        response = cur.fetchone()
        
        if response:
            return True
        return False
