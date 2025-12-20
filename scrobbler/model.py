import hashlib
import time
import pylast
import DBcm
import platform

# Database configuration
def get_db_config():
    if "aws" in platform.uname().release:
        return {
            "user": "scrobbler",
            "password": "scrobpasswd",
            "host": "scrobbler.mysql.pythonanywhere-services.com",
            "database": "scrobbler$default",
        }
    else:
        return {
            "user": "scrobbleruser",
            "password": "scrobblerpasswd",
            "host": "localhost",
            "database": "scrobbler",
        }

creds = get_db_config()

class DatabaseModel:
    @staticmethod
    def get_credentials_by_username(username):
        SQL = "SELECT * FROM creds WHERE username = %s"
        with DBcm.UseDatabase(creds) as db:
            db.execute(SQL, (username,))
            result = db.fetchone()
        return result

    @staticmethod
    def save_credentials(api_key, api_secret, username, password):
        # Hash the password before storing (MD5 for Last.fm compatibility)
        pass_has = hashlib.md5(password.encode()).hexdigest()
        # Check if username already exists
        existing = DatabaseModel.get_credentials_by_username(username)
        if existing:
            # Update existing credentials
            SQL = """
                UPDATE creds
                SET api_key = %s, api_secret = %s, pass_has = %s
                WHERE username = %s
            """
            with DBcm.UseDatabase(creds) as db:
                db.execute(SQL, (api_key, api_secret, pass_has, username))
        else:
            # Insert new credentials
            SQL = """
                INSERT INTO creds (api_key, api_secret, username, pass_has)
                VALUES (%s, %s, %s, %s)
            """
            with DBcm.UseDatabase(creds) as db:
                db.execute(SQL, (api_key, api_secret, username, pass_has))

    @staticmethod
    def verify_login(username, password):
        credentials = DatabaseModel.get_credentials_by_username(username)
        if not credentials:
            return False

        # Hash the provided password and compare with stored hash
        provided_hash = hashlib.md5(password.encode()).hexdigest()
        stored_hash = credentials[4]  # pass_has is at index 4

        return provided_hash == stored_hash


class LastFMModel:
    def __init__(self, api_key, api_secret, username, password_hash):
        self.network = pylast.LastFMNetwork(
            api_key=api_key,
            api_secret=api_secret,
            username=username,
            password_hash=password_hash
        )

    def scrobble_album(self, artist, album):
        # Get album and tracks
        album_obj = self.network.get_album(artist, album)
        tracks = album_obj.get_tracks()

        # Scrobble all tracks with timestamps
        current_time = int(time.time())
        for i, track in enumerate(tracks):
            timestamp = current_time - (len(tracks) - i) * 30
            self.network.scrobble(
                artist=artist,
                title=track.title,
                album=album,
                timestamp=timestamp
            )

        return len(tracks)