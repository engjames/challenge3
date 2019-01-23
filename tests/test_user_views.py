from tests.base import BaseTestCase
from app.models.user_model import User
from app import conn
import unittest
import json
import time
import string
import random

def email_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class TestAuthBluePrint(BaseTestCase):
    def test_user_registration(self):
        """
        Test a user is successfully created through the api
        :return:
        """
        with self.client:
            response = self.register_user('Kisuule','James','abc@gmail.com', '123456', 'true')
            data = json.loads(response.data.decode())
            if data['status'] == 201:
                self.assertTrue(response.content_type == 'application/json')
                self.assertEqual(response.status_code, 201)
            else:
                response = self.register_user('Kisuule','James',email_generator()+'@gmail.com', '123456', 'true')
                data = json.loads(response.data.decode())
                self.assertTrue(data['status'] == 201)
                self.assertTrue(response.content_type == 'application/json')
                self.assertEqual(response.status_code, 201)

    def test_user_registration_fails_if_content_type_not_json(self):
        """
        Test the content type is application/json
        :return:
        """
        with self.client:
            response = self.register_user_with_wrong_request_content_type('Kisuule','james','abc@gmail.com', '123456', 'true')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 400)
            self.assertTrue(data['error'] == 'Content-type must be json')
            self.assertEqual(response.status_code, 400)

    def register_user_with_wrong_request_content_type(self, firstname, lastname, email, password, isAdmin):
        """
        Helper method to register a user using a wrong content-type
        :param email: Email
        :param password: Password
        :return:
        """
        return self.client.post(
            'auth/signup',
            content_type='application/javascript',
            data=json.dumps(dict(firstname=firstname, lastname=lastname, email=email, password=password, isAdmin=isAdmin)))
    
    def test_user_registration_missing_email_or_and_password(self):
        """
        Test that the email and password are set when sending the request
        :return:
        """
        with self.client:
            response = self.register_user("james", "Kisuule", "", "", "true")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 400)
            # assert data['error'] == 'Missing or wrong email format or password is less than five characters'
            self.assertTrue(data['error'] == 'Missing or wrong email format or password is less than five characters')

    def test_user_email_validity(self):
        """
        Check that the user has supplied a valid email address.
        :return:
        """
        with self.client:
            response = self.register_user("james", "Kisuule","john", "123456","true")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 400)
            self.assertTrue(data['error'] == "Missing or wrong email format or password is less than five characters")

    def test_user_password_length_is_greater_than_four_characters(self):
        with self.client:
            response = self.register_user("james", "Kisuule","john@gmail.com", "123", "true")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 400)
            self.assertTrue(data['error'] == "Missing or wrong email format or password is less than five characters")
    
    def test_user_is_already_registered(self):
        """
        Test that the user already exists.
        :return:
        """
        user = User('Kisuule','James','example@gmail.com', '123456', 'true')
        user.save()

        with self.client:
            response = self.register_user('Kisuule','James','example@gmail.com', '123456', 'true')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 400)
            self.assertTrue(data['error'] == 'Failed, User already exists, Please sign In')
            self.assertEqual(response.status_code, 400)

    def test_user_can_login(self):
        """
        Register and login in a user
        :return:
        """
        with self.client:
            self.register_and_login_in_user()


    def test_login_has_incorrect_email_and_valid_length_password(self):
        """
        Test the email of the user trying to login is valid and the password length is greater than 4 characters
        :return:
        """
        with self.client:
            response = self.login_user('johngmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertTrue(response.content_type == 'application/json')
        
                                                

    def test_user_trying_to_login_does_not_exist_or_passwords_do_not_much(self):
        """
        Test that the user does not exist or the password is incorrect
        :return:
        """
        with self.client:
            response = self.login_user('john123@gmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 401)
    

    def login_user(self, email, password):
        """
        Helper method to login a user
        :param email: Email
        :param password: Password
        :return:
        """
        return self.client.post(
            '/auth/login',
            content_type='application/json',
            data=json.dumps(dict(email=email, password=password)))

    def register_and_login_in_user(self):
        """
        Helper method to sign up and login a user
        :return: Json login response
        """
        email1 =email_generator()+'@gmail.com' 
        reg_response = self.register_user('Kisuule','James',email1, '123456', 'true')
        data = json.loads(reg_response.data.decode())
        self.assertTrue(data['status'] == 201)
        self.assertTrue(reg_response.content_type == 'application/json')
        self.assertEqual(reg_response.status_code, 201)
        # Login the user
        login_response = self.client.post(
            'auth/login',
            data=json.dumps(dict(email=email1, password='123456')),
            content_type='application/json'
        )
        login_data = json.loads(login_response.data.decode('utf-8'))
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_data['data'][0]['token'])
        self.assertTrue(login_data['status'] == 200)
        self.assertTrue(login_response.content_type == 'application/json')
        return login_data

    
  

    