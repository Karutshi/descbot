import psycopg2
from functools import wraps
from datetime import datetime

def cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cur = self.conn.cursor()
        result = func(self, cur, *args, **kwargs)
        cur.close()
        self.conn.commit()
        return result
    return wrapper

class DatabaseHandler:
    

    def __init__(self):
        self.conn = psycopg2.connect("dbname='descbot' user='postgres' password='postgres'")
    
    @cursor
    def check_in(self, cur, userId, channelName):
        time = datetime.now()
        query = "INSERT INTO online VALUES (%s, %s, %s);"
        cur.execute(query, (userId, channelName, time))

    @cursor
    def check_out(self, cur, userId):
        cur.execute("DELETE FROM online WHERE id=%s RETURNING channel, joined;", (userId,))
        channel, joined = cur.fetchone()
        print((channel, joined))
        time = datetime.now() - joined
        cur.execute("UPDATE times SET time=time+%s WHERE id=%s AND channel=%s;", (time, userId, channel))
        cur.execute("INSERT INTO times (id, channel, time)" +
                    "SELECT %s, %s, %s WHERE NOT EXISTS (" +
                    "SELECT id, channel FROM times WHERE id=%s AND channel=%s);", 
                    (userId, channel, time, userId, channel))
        
