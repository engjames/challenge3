from flask.views import MethodView
from flask import request,jsonify
from app.views.helper import token_required, response,response_for_user_incidents
from app.models.incidents_model import CreateRecord
from app import conn
#create a cursor objects for executing our sql statements
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

        #let's return all incidents if the incident_id is None
        if incident_id is None:
            #It's only the admin that can execute this endpoint. lets use the enail to get the user type
            sql = """SELECT isadmin FROM users WHERE email=%s"""
            cur = conn.cursor()
            cur.execute(sql,(current_user,))
            user_record = cur.fetchone()
            user_type= user_record[0]
            #verify if isAdmin is true
            if user_type == "true":
                
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
                            'createdby': row[1],
                            'category':row[2],
                            'title':row[3],
                            'comment':row[4],
                            'location':row[5],
                            'status':row[6],
                            'createdOn':row[7]
                        }
                        all_incidents.append(incident)

                    return response_for_user_incidents('success', all_incidents, 200)
                return response('success', "There exists no incidents", 200)
            return response('failed', 'Sorry, this request requires administrative privileges to run', 401)
                
        #this point is reached if the user has provided the incident_id
        #lets check if it is a valid id
        try:
            int(incident_id)
        #if we can't convert it to an integer, let's return the exception message below
        except ValueError:
            return response('failed', 'Please provide a valid Incident Id', 400)
        #lets continue if we can change the incident-id to integer
        else:
            #lets select the record matching the given incident_id
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
                        'title':row[3],
                        'comment':row[4],
                        'location':row[5],
                        'status':row[6],
                        'createdOn':row[7]
                    }

                return response_for_user_incidents('success', user_incident, 200)
            return response('failed', "Incident not found", 404) 
    
                
    @token_required
    def post(current_user, self):
        """
        Method for creating the new incident
        """
        #check if the posted dat has a content type of json
        if request.content_type == 'application/json':
            #get all posted data in the request that is in form of json
            post_data = request.get_json()
            title = post_data.get('title')
            category = post_data.get('category')
            comment = post_data.get('comment')
            location = post_data.get('location')
    
            #check if all posted data is in form of a string as required in the document
            if isinstance(category,str) and isinstance(comment,str) and isinstance(location,str) and isinstance(title,str):
                #check if the intervention record doesn't exist
                #current_user contains email, lets use the email to get the user id
                cur = conn.cursor()
                sql1 = """
                    SELECT user_id FROM users WHERE email=%s 
                """
                cur.execute(sql1,(current_user,))
                user = cur.fetchone()
                # Extract the user_id from the returned data 
                user_id = user[0]
                #call a method under create record modal to check for title of the intervention record
                incident = CreateRecord.get_by_name(user_id,title)

                #lets create the intervention record if it doesnt exist
                if not incident:
                    CreateRecord(user_id, title, category, comment, location).save()
                    return response('success', 'Incident created successfully', 201)
                return response('failed', 'Failed, Incident already exists, Please wait as they work on it', 400)
            return response('failed', 'Category, comment and location should be a string', 400)
        return response('failed', 'Content-type must be json', 202)                   

    @token_required   
    def put(current_user, self, incident_id):
        """
        Method for the location
        """
        #lets check if it is a valid id
        try:
            int(incident_id)
        #if we can't convert it to an integer, let's return the exception message below
        except ValueError:
            return response('failed', 'Please provide a valid Incident Id', 400)
        
        if 'location' not in request.json:
            return jsonify({"status": 400, "data":[{"error-message" : "wrong body format. follow this example ->> {'location':'[8.9090,56.2200]'}"}]})
        
        if not isinstance(request.json['location'], str):
            return jsonify({"status":400, "data": [{"error-message" : "Location must a string"}]})

        cur = conn.cursor()
        sql1 = """
            SELECT user_id FROM users WHERE email=%s 
        """
        cur.execute(sql1,(current_user,))
        user = cur.fetchone()
        #get users id w/c is in position 0 of the returned list
        user_id = user[0]

        #check for the record matching the user's id and incident id
        cur = conn.cursor()
        sql2 = """
            SELECT * FROM incidents WHERE createdby=%s AND incident_id=%s 
        """
        cur.execute(sql2,(user_id, int(incident_id)))
        incident_record = cur.fetchone()
        
        #if there is no matching record
        if not incident_record:
            return jsonify({"status":404, "data": [{"error-message" : "No intervention record found with this id"}]})
        
        #we can not delete a record with statuses of 'under investigation','rejected','resolved'
        #get the status which is in position 6 of the returned list
        status = incident_record[6]
        if status in ['under investigation','rejected','resolved']:
            return jsonify({"status":400, "data": [{"error-message" : "You can no longer edit or delete this intervention"}]})
        #call a method under create record that deletes the record. it takes in the users id and incident id
        CreateRecord.update_location(user_id, int(incident_id), location=request.json['location'])
        return jsonify({"status":400, "data":[{"id":int(incident_id), "message":"Updated red-flag record’s location"}]})
        

    @token_required
    def delete(current_user,self, incident_id):
        try:
            int(incident_id)
        except ValueError:
            return response('failed', 'Please provide a valid Incident Id', 400)
        
        #Current user contains the email, lets use the email to get the user's id
        cur = conn.cursor()
        sql1 = """
            SELECT user_id FROM users WHERE email=%s 
        """
        cur.execute(sql1,(current_user,))
        user = cur.fetchone()
        #get users id w/c is in position 0 of the returned list
        user_id = user[0]

        #check for the record matching the user's id and incident id
        cur = conn.cursor()
        sql2 = """
            SELECT * FROM incidents WHERE createdby=%s AND incident_id=%s 
        """
        cur.execute(sql2,(user_id, int(incident_id)))
        incident_record = cur.fetchone()
        
        
        #if there is no matching record
        if not incident_record:
            return jsonify({"status":404, "data": [{"error-message" : "No intervention record found with this id"}]})
        
        #we can not delete a record with statuses of 'under investigation','rejected','resolved'
        #get the status which is in position 6 of the returned list
        status = incident_record[6]
        if status in ['under investigation','rejected','resolved']:
            return jsonify({"status":400, "data": [{"error-message" : "You can no longer edit or delete this red-flag"}]})
        #call a method under create record that deletes the record. it takes in the users id and incident id
        CreateRecord.delete(user_id,int(incident_id))
        return jsonify({"status":200, "data":[{"id":int(incident_id), "message":"Intervention record has been deleted"}]})


class InterventionComment(MethodView):
    @token_required   
    def put(current_user, self, incident_id):
        """
        Method for the status
        """
        #lets check if it is a valid id
        try:
            int(incident_id)
        #if we can't convert it to an integer, let's return the exception message below
        except ValueError:
            return response('failed', 'Please provide a valid Incident Id', 400)
        
        if 'comment' not in request.json:
            return jsonify({"status": 400, "data":[{"error-message" : "wrong body format. follow this example ->> {'comment':'Repair roads'}"}]})
        
        if not isinstance(request.json['comment'], str):
            return jsonify({"status":400, "data": [{"error-message" : "Comment must a string"}]})

        cur = conn.cursor()
        sql1 = """
            SELECT user_id FROM users WHERE email=%s 
        """
        cur.execute(sql1,(current_user,))
        user = cur.fetchone()
        #get users id w/c is in position 0 of the returned list
        user_id = user[0]

        #check for the record matching the user's id and incident id
        cur = conn.cursor()
        sql2 = """
            SELECT * FROM incidents WHERE createdby=%s AND incident_id=%s 
        """
        cur.execute(sql2,(user_id, int(incident_id)))
        incident_record = cur.fetchone()
        
        #if there is no matching record
        if not incident_record:
            return jsonify({"status":404, "data": [{"error-message" : "No intervention record found with this id"}]})
        
        #we can not delete a record with statuses of 'under investigation','rejected','resolved'
        #get the status which is in position 6 of the returned list
        status = incident_record[6]
        if status in ['under investigation','rejected','resolved']:
            return jsonify({"status":400, "data": [{"error-message" : "You can no longer edit or delete this intervention"}]})
        #call a method under create record that deletes the record. it takes in the users id and incident id
        CreateRecord.update_comment(user_id, int(incident_id), comment=request.json['comment'])
        return jsonify({"status":400, "data":[{"id":int(incident_id), "message":"Updated red-flag record’s comment"}]})

class InterventionStatus(MethodView):
    
    @token_required   
    def put(current_user, self, incident_id):
        """
        Method for the status
        """
        #It's only the admin that can execute this endpoint. lets use the enail to get the user type
        sql = """SELECT isadmin FROM users WHERE email=%s"""
        cur = conn.cursor()
        cur.execute(sql,(current_user,))
        user_record = cur.fetchone()
        user_type= user_record[0]
        #verify if isAdmin is true
        if not user_type == "true":
            return response('failed', 'Sorry, this request requires administrative privileges to run', 401)    

        #lets check if it is a valid id
        try:
            int(incident_id)
        #if we can't convert it to an integer, let's return the exception message below
        except ValueError:
            return response('failed', 'Please provide a valid Incident Id', 400)
        
        if 'status' not in request.json:
            return jsonify({"status": 400, "data":[{"error-message" : "wrong body format. follow this example ->> {'status':'Resolved'}"}]})
        
        if not isinstance(request.json['status'], str):
            return jsonify({"status":400, "data": [{"error-message" : "Status must a string"}]})

        cur = conn.cursor()
        sql1 = """
            SELECT user_id FROM users WHERE email=%s 
        """
        cur.execute(sql1,(current_user,))
        user = cur.fetchone()
        #get users id w/c is in position 0 of the returned list
        user_id = user[0]

        #check for the record matching the user's id and incident id
        cur = conn.cursor()
        sql2 = """
            SELECT * FROM incidents WHERE incident_id=%s 
        """
        id = int(incident_id)
        cur.execute(sql2,(id,))
        incident_record = cur.fetchone()
        
        #if there is no matching record
        if not incident_record:
            return jsonify({"status":404, "data": [{"error-message" : "No intervention record found with this id"}]})
        
        #we can not delete a record with statuses of 'under investigation','rejected','resolved'
        #get the status which is in position 6 of the returned list
        status = request.json['status']
        if status.lower() not in ['under investigation','rejected','resolved']:
            return jsonify({"status":400, "data": [{"error-message" : "The status can either be 'under investigation', 'rejected', or 'resolved'"}]})
        #call a method under create record that deletes the record. it takes in the users id and incident id
        CreateRecord.update_status(user_id, int(incident_id), status)
        return jsonify({"status":400, "data":[{"id":int(incident_id), "message":"Updated intervention record’s status"}]})



#generating routes for our endpoints
class GetIncidentUrls:
    @staticmethod
    def fetch_urls(app):
        # Register classes as view methods so that we can tell if we're working with a post or put or delete or put
        incident_view = Incident.as_view('incident_api')
        edit_comment_view = InterventionComment.as_view('edit_comment')
        update_status_view = InterventionStatus.as_view('edit_status')

        app.add_url_rule('/interventions', defaults={'incident_id': None},
                         view_func=incident_view, methods=['GET',])
        app.add_url_rule('/interventions', view_func=incident_view, methods=['POST',])
        app.add_url_rule('/interventions/<incident_id>', view_func=incident_view, methods=['GET', 'DELETE',])
        app.add_url_rule('/interventions/<incident_id>/location', view_func=incident_view, methods=['PUT',])
        app.add_url_rule('/interventions/<incident_id>/comment', view_func=edit_comment_view, methods=['PUT',])
        app.add_url_rule('/interventions/<incident_id>/status', view_func=update_status_view , methods=['PUT',])
        