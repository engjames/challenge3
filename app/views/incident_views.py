from flask.views import MethodView
from flask import request,jsonify
from app.views.helper import token_required, response,response_for_user_incidents
from app.models.incidents_model import CreateRecord
from app import conn

cur = conn.cursor()

class Incident(MethodView):
    """
    Class Incident defines the restApi methods.
    """
    @token_required
    def get(current_user,self, incident_id):
        """
        Return all incidents if incident id is None or return an incident with the supplied incident Id.
        :param current_user: User
        :param incident_id: 
        :return:
        """
        sql = """SELECT isadmin FROM users WHERE email=%s"""
        cur = conn.cursor()
        cur.execute(sql,(current_user,))
        user_record = cur.fetchone()
        user_type= user_record[0]
        if user_type == "true":
            if incident_id is None:
                cur = conn.cursor()
                sql = """
                    SELECT * FROM incidents
                """
                cur.execute(sql)
                rows = cur.fetchall()
                all_incidents = []
                if rows:
                    for row in rows:
                        incident = {
                            'incident_id': row[0],
                            'user_id': row[1],
                            'title':row[3],
                            'comment':row[4],
                            'location':row[5],
                            'status':row[6],
                            'createdOn':row[7]
                        }
                        all_incidents.append(incident)

                    return response_for_user_incidents('success', all_incidents, 200)
                return response('success', "There exists no incidents", 200)
            

            try:
                int(incident_id)
            except ValueError:
                return response('failed', 'Please provide a valid Incident Id', 400)
            else:
                cur = conn.cursor()
                sql = """
                    SELECT * FROM incidents WHERE incident_id=%s
                """
                cur.execute(sql,(incident_id,))
                row = cur.fetchone()
                if row:
                    user_incident = incident = {
                            'incident_id': row[0],
                            'user_id': row[1],
                            'category':row[2],
                            'comment':row[3],
                            'location':row[4],
                            'status':row[5],
                            'createdOn':row[6]
                        }

                    return response_for_user_incidents('success', user_incident, 200)
                return response('failed', "Incident not found", 404) 
        return response('failed', 'Sorry, this request requires administrative privileges to run', 401)
                
    @token_required
    def post(current_user, self):
        """
        Method for creating the new incident record
        """
        if request.content_type == 'application/json':
            post_data = request.get_json()
            title = post_data.get('title')
            category = post_data.get('category')
            comment = post_data.get('comment')
            location = post_data.get('location')
    
            if isinstance(category,str) and isinstance(comment,str) and isinstance(location,str) and isinstance(title,str):
                cur = conn.cursor()
                sql1 = """
                    SELECT user_id FROM users WHERE email=%s 
                """
                cur.execute(sql1,(current_user,))
                user = cur.fetchone()
                user_id = user[0]
                incident = CreateRecord.get_by_name(user_id,title)
                if not incident:
                    CreateRecord(user_id, title, category, comment, location).save()
                    return response('success', 'Incident created successfully', 201)
                return response('failed', 'Failed, Incident already exists, Please wait as they work on it', 400)
            return response('failed', 'Category, comment, title and location should be a string', 400)
        return response('failed', 'Content-type must be json', 202)                   

    @token_required   
    def put(current_user, self, incident_id):
        """
        Method for updating the incident status
        """
        if current_user == "admin@admin.com":
            try:
                int(incident_id)
            except ValueError:
                return response('failed', 'Please provide a valid Incident Id', 400)
            else:
                cur = conn.cursor()
                sql1 = """
                    SELECT incident_id FROM incidents WHERE incident_id=%s 
                """
                cur.execute(sql1,(incident_id,))
                incident = cur.fetchone()
                if incident:
                    if request.content_type == 'application/json':
                        post_data = request.get_json()
                        incident_status =  post_data.get('status')
                        if incident_status:
                            if isinstance(incident_status,str):
                                if incident_status in ["New","Processing","Cancelled","Complete"]:
                                    CreateRecord.update(status, incident_id)
                                    return response('success', 'Incident Status successfully updated',201)
                                return response('failed', 'The Status of an incident could either be draft , Resolved, Rejected or Under investigation .', 400)          
                            return response('failed', 'Incident status should be a string', 400)
                        return response('failed', 'Incident status cannot be empty', 400)
                    return response('failed', 'Content-type must be json', 202)
                return response('failed', 'The incident with that id doesnt exist', 404)
        return response('failed', 'Sorry, this request requires administrative privileges to run', 401)



class GetIncidentUrls:
    @staticmethod
    def fetch_urls(app):
        # Register classes as views
        incident_view = Incident.as_view('incident_api')
        app.add_url_rule('/incidents', defaults={'incident_id': None},
                         view_func=incident_view, methods=['GET',])
        app.add_url_rule('/users/incidents', view_func=incident_view, methods=['POST',])
        app.add_url_rule('/incidents/<incident_id>', view_func=incident_view, methods=['GET', 'PUT', 'DELETE',])
        app.add_url_rule('/admin/incidents/<incident_id>', view_func=incident_view, methods=['PUT',])
        