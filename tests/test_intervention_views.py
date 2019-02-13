from tests.base import BaseTestCase
from app.models.user_model import User
from app import conn
import unittest
import json


class TestInterventionBluePrint(BaseTestCase):
    def test_intervention_creation(self):
        """
        Test an intervention is successfully created through the api
        :return:
        """
        with self.client:
            response = self.create_intervention()
            data = json.loads(response.data.decode('utf-8'))
            if data['status'] == 201:
                self.assertTrue(data['status'] == 201)
                self.assertTrue(data['data'][0]['Message'] == "Created intervention record")
                self.assertTrue(response.content_type == 'application/json')
                self.assertEqual(response.status_code, 201)
            elif data['error'] == "Incident already exists, Please wait as they work on it":
                self.assertTrue(data['status'] == 400)
                self.assertTrue(data['error'] == "Incident already exists, Please wait as they work on it")
                self.assertTrue(response.content_type == 'application/json')
                self.assertEqual(response.status_code, 400)
    

    def test_get_a_specific_intervention(self):
        """
        Test function to get a specific intervention record
        :return:
        """
        token = self.get_user_token()
        response = self.client.get('interventions/1',headers={"auth_token": token},content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        if response.status_code == 404:
            self.assertEqual(data['status'], 404)
            self.assertEqual(data['error'], 'Incident not found')
            self.assertEqual(response.status_code, 404)
        elif  response.status_code == 200:
            self.assertEqual(data['status'], 200)
            self.assertEqual(response.status_code, 200)
    
    def test_update_intervention_location(self):
        """
        Test function to update intervention location
        :return:
        """
        token = self.get_user_token()
        response = self.client.put('/interventions/1/location',headers={"auth_token": token}, data=json.dumps({"location":"[0.8080,4.5321]"}), content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        # assert data == 200
        self.assertEqual(data['status'], 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data'][0]['message'], 'Updated intervention record’s location')
        
    def test_update_intervention_comment(self):
        """
        Test function to update intervention comment
        :return:
        """
        token = self.get_user_token()
        response = self.client.put('/interventions/1/comment',headers={"auth_token": token}, data=json.dumps({"comment":"Bribery", "location":"1,4"}), content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        # assert data == 200
        self.assertEqual(data['status'], 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data'][0]['message'], 'Updated intervention records')

    def test_update_intervention_status(self):
        """
        Test function to update intervention comment
        :return:
        """
        token = self.get_admin_token()
        response = self.client.put('/interventions/1/status',headers={"auth_token": token}, data=json.dumps({"status":"resolved"}), content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        # assert data == 200
        self.assertEqual(data['status'], 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data'][0]['message'], 'Updated intervention record’s status')
    
