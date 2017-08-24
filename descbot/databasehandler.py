import psycopg2
from functools import wraps
from datetime import datetime, timedelta

def cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.connect() as conn:
            cur = conn.cursor()
            result = func(self, cur, *args, **kwargs)
        return result
    return wrapper

class DatabaseHandler:
   
    def connect(self):
        return psycopg2.connect("dbname='descbot' user='postgres' password='postgres'")
 
    @cursor
    def check_in(self, cur, userId, channelName):
        time = datetime.now()
        query = "INSERT INTO online VALUES (%s, %s, %s);"
        cur.execute(query, (userId, channelName, time))

    @cursor
    def check_out(self, cur, userId, time = None):
        cur.execute("DELETE FROM online WHERE id=%s RETURNING channel, joined;", (userId,))
        channel, joined = cur.fetchone()
        time = (datetime.now() if time is None else time) - joined
        cur.execute("UPDATE times SET time=time+%s WHERE id=%s AND channel=%s;", (time, userId, channel))
        cur.execute("INSERT INTO times (id, channel, time)" +
                    "SELECT %s, %s, %s WHERE NOT EXISTS (" +
                    "SELECT id, channel FROM times WHERE id=%s AND channel=%s);", 
                    (userId, channel, time, userId, channel))
    
    @cursor
    def check_everyone_out(self, cur, time = None):
        cur.execute("DELETE FROM online RETURNING id, channel, joined;")
        result = cur.fetchall()
        for userId, channel, joined in result:
            insert_time = (datetime.now() if time is None else time) - joined 
            cur.execute("UPDATE times SET time=time+%s WHERE id=%s AND channel=%s;", (insert_time, userId, channel))
            cur.execute("INSERT INTO times (id, channel, time)" +
                        "SELECT %s, %s, %s WHERE NOT EXISTS (" +
                        "SELECT id, channel FROM times WHERE id=%s AND channel=%s);", 
                    (userId, channel, insert_time, userId, channel))
      
        

    @cursor
    def get_user_stats(self, cur, userId, amount):
        query = "SELECT channel, time, joined FROM "\
                "times FULL OUTER JOIN online "\
                "USING (id, channel) "\
                "WHERE id = %s;"
        online_time = lambda x: datetime.now() - x if x is not None else timedelta(seconds = 0)
        safe_time = lambda x: x if x is not None else timedelta(seconds = 0)
        cur.execute(query, (userId,))
        stats = [(channel, safe_time(time) + online_time(joined)) for channel, time, joined in cur]
        print(stats)
        for row in sorted(stats, key = lambda x: -x[1])[:amount]:
            yield row

    @cursor
    def get_stats(self, cur, amount):
        query = "SELECT id, SUM(time), MIN(joined) FROM "\
                "times FULL OUTER JOIN online "\
                "USING (id) "\
                "GROUP BY id;"
        now = datetime.now()
        online_time = lambda x: now - x if x is not None else timedelta(seconds = 0)
        safe_time = lambda x: x if x is not None else timedelta(seconds = 0)
        cur.execute(query)
        stats = [(uid, safe_time(time) + online_time(joined)) for uid, time, joined in cur]
        for row in sorted(stats, key = lambda x: -x[1])[:amount]:
            yield row

    @cursor
    def get_user_total(self, cur, userId):
        query = "SELECT id, SUM(time), MIN(joined) FROM "\
                "times FULL OUTER JOIN online "\
                "USING (id) "\
                "WHERE id = %s "\
                "GROUP BY id;"
        cur.execute(query, (userId,))
        online_time = lambda x: datetime.now() - x if x is not None else timedelta(seconds = 0)
        uid, time, joined = cur.fetchone()
        time = time if time is not None else timedelta(seconds = 0)
        return time + online_time(joined)
