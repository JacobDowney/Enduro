import sqlite3

class DB_Handler():
    def __init__(self):
        self.db = 'storage.db'

    def create_tables(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE enduro_attempts (
                id                      text,
                enduro_name             text,
                name                    text,
                description             text,
                device_name             text,
                distance                integer,
                elapsed_time            integer
                total_elevation_gain    integer,
                kudos_count             integer,
                max_speed               integer,
                calories                integer,
                photos                  text,
                gear                    text,
                enduro_time             integer
            )
        """)
        cursor.execute("""
            CREATE TABLE segment_efforts (
                id                  text,
                segment_id          text,
                name                text,
                distance            integer,
                elapsed_time        integer,
                average_watts       integer,
                average_heartrate   integer,
                max_heartrate       integer
            )
        """)
        cursor.execute("""
            CREATE TABLE enduro_to_segment (
                enduro_attempt_id   text,
                segment_effort_id   text
            )
        """)
        conn.commit()
        conn.close()

    def insert_enduros(self, enduros):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        # Format all the enduros and segments
        formatted_enduros = []
        formatted_segments = []
        formatted_enduros_to_segments = []
        for enduro_name in enduros:
            e = enduros[enduro_name]
            formatted_enduro = (e.id, enduro_name, e.name, e.description,
                e.device_name, e.distance, e.elapsed_time,
                e.total_elevation_gain, e.kudos_count, e.max_speed, e.calories,
                e.photos, e.gear, e.enduro_time)
            formatted_enduros.append(formatted_enduro)
            for key in e.segment_attempts:
                s = e.segment_attempts[key]
                formatted_segment = (s.id, s.segment_id, s.name, s.distance,
                    s.elapsed_time, s.average_watts, s.average_heartrate,
                    s.max_heartrate)
                formatted_segments.append(formatted_segment)
                formatted_enduro_to_segment = (e.id, s.id)
                formatted_enduros_to_segments.append(formatted_enduro_to_segment)
        # Insert formatted enduros and segments into their tables
        cursor.executemany("INSERT INTO enduro_attempts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", formatted_enduros)
        cursor.executemany("INSERT INTO segment_efforts VALUES (?,?,?,?,?,?,?,?)", formatted_segments)
        cursor.executemany("INSERT INTO enduro_to_segment VALUES (?,?)", formatted_enduros_to_segments)
        conn.commit()
        conn.close()

    def get_enduros(self, enduro_name):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # TODO(downeyj) validate if this is how you plug in variable
        cursor.execute("SELECT * FROM enduro_attempts WHERE enduro_name = (?)", enduro_name)
        results = cursor.fetchall()

        conn.commit()
        conn.close()
