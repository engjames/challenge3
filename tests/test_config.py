from flask_testing import TestCase
from app import app
from flask import current_app
import unittest
import os


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        """
        Create an app with the development configuration
        :return:
        """
        app.config.from_object('app.config.DevelopmentConfig')
        return app

    def test_app_in_development(self):
        """
        Test that the development configs are set correctly.
        :return:
        """
        self.assertTrue(app.config['SECRET_KEY'] is 'thisissecret')
        self.assertTrue(app.config['DEBUG'], True)
        self.assertFalse(current_app is None)
       


class TestTestingConfig(TestCase):
    def create_app(self):
        """
        Create an instance of the app with the testing configuration
        :return:
        """
        app.config.from_object('app.config.TestingConfig')
        return app

    def test_app_in_testing(self):
        """
        Test that the testing configs are set correctly
        :return:
        """
        self.assertTrue(app.config['SECRET_KEY'] is 'thisissecret')
        self.assertTrue(app.config['DEBUG'], True)
        self.assertTrue(app.config['TESTING'] is True)
        self.assertFalse(current_app is None)
    


if __name__ == '__main__':
    unittest.main()
