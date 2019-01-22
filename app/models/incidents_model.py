from app import conn

cur = conn.cursor()

class CreateRecord():
    cur.execute("""CREATE TABLE IF NOT EXISTS incidents (
                incident_id SERIAL PRIMARY KEY,
                createdBy INTEGER NOT NULL,
                category VARCHAR(100) NOT NULL,
                title VARCHAR(100) NOT NULL,
                comment VARCHAR(100) NOT NULL,
                location VARCHAR(100) NOT NULL,
                status VARCHAR(100)  DEFAULT 'draft',
                createdOn TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (createdBy)
                    REFERENCES users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            """)
    def __init__(self, user_id, title, category, comment, location):
        self.user_id = user_id
        self.title = title 
        self.category = category
        self.comment = comment
        self.location = location

    def save(self):
        cur = conn.cursor()
        sql = """
            INSERT INTO incidents (createdBy, title, category, comment, location) 
                    VALUES (%s,%s,%s,%s,%s)
        """
        cur.execute(sql,(self.user_id, self.title, self.category, self.comment, self.location,))
        conn.commit()
        
    @staticmethod
    def update_location(user_id, incident_id, location):
        cur = conn.cursor()
        sql = """
            UPDATE incidents set location = %s WHERE incident_id = %s
            """
        cur.execute(sql,(location, incident_id,))
        conn.commit()
    
    @staticmethod
    def update_comment(user_id, incident_id, comment):
        cur = conn.cursor()
        sql = """
            UPDATE incidents set comment = %s WHERE incident_id = %s
            """
        cur.execute(sql,(comment, incident_id,))
        conn.commit()
    @staticmethod
    def update_status(user_id, incident_id, status):
        cur = conn.cursor()
        sql = """
            UPDATE incidents set status = %s WHERE incident_id = %s
            """
        cur.execute(sql,(status, incident_id,))
        conn.commit()

    @staticmethod
    def delete(user_id,incident_id):
        cur = conn.cursor()
        sql2 = """
            DELETE FROM incidents WHERE createdby=%s AND incident_id=%s 
        """
        cur.execute(sql2,(user_id, incident_id))
        conn.commit()

    @staticmethod
    def get_by_name(user_id,title):
        """
        Filter incidents by title.
        :param category:
        :return: User or None
        """
        cur = conn.cursor()
        sql1 = """
             SELECT * FROM incidents WHERE createdBy=%s AND title=%s AND status=%s
        """
        cur.execute(sql1,(user_id,title,"draft",))
        category1 = cur.fetchone()
        return category1


