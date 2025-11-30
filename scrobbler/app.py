from flask import Flask, render_template, request, session, redirect, url_for
import pylast
import hashlib
import time
import DBcm
import platform

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
if "aws" in platform.uname().release:
    creds = {
        "user": "scrobbler",
        "password": "scrobpasswd",
        "host": "scrobbler.mysql.pythonanywhere-services.com",
        "database": "scrobbler$default",
    }
else:
    creds = {
        "user": "scrobbleruser",
        "password": "scrobblerpasswd",
        "host": "localhost",
        "database": "scrobbler",
    }


def get_credentials_by_username(username):
    """Retrieves credentials for a specific username."""
    SQL = "SELECT * FROM creds WHERE username = %s"
    with DBcm.UseDatabase(creds) as db:
        db.execute(SQL, (username,))
        result = db.fetchone()
    return result

def save_credentials(api_key, api_secret, username, password):
    """Inserts or updates credentials in the 'creds' table."""
    # Hash the password before storing
    pass_has = hashlib.md5(password.encode()).hexdigest()

    # Check if username already exists
    existing = get_credentials_by_username(username)

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

def verify_login(username, password):
    """Verifies username and password against stored credentials."""
    credentials = get_credentials_by_username(username)
    if not credentials:
        return False

    # Hash the provided password and compare with stored hash
    provided_hash = hashlib.md5(password.encode()).hexdigest()
    stored_hash = credentials[4]  # pass_has is at index 4

    return provided_hash == stored_hash

@app.get("/")
def opening_page():
    # Check if user is logged in
    if 'username' in session:
        return render_template("scrobble.html", the_title="Scrobble Album", username=session['username'])
    else:
        return render_template("login.html", the_title="Login to Scrobbler")

@app.get("/setup")
def setup_page():
    return render_template("setup.html", the_title="Setup Credentials")

@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]

    if verify_login(username, password):
        session['username'] = username
        return "Login successful! You can now scrobble albums."
    else:
        return "Error: Invalid username or password."

@app.post("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")

@app.post("/savesetup")
def save_credentials_route():
    # Get form data
    api_key = request.form["api_key"]
    api_secret = request.form["api_secret"]
    username = request.form["username"]
    password = request.form["password"]

    # Save to database
    save_credentials(api_key, api_secret, username, password)

    return "Credentials saved! You can now login to scrobble albums."

@app.post("/scrobble")
def scrobble_album():
    # Check if user is logged in
    if 'username' not in session:
        return "Error: Please login first."

    username = session['username']

    # Get credentials from database
    credentials = get_credentials_by_username(username)
    if not credentials:
        return "Error: No credentials found for your account. Please set up credentials first."

    # credentials tuple: (id, api_key, api_secret, username, pass_has)
    api_key, api_secret, pass_has = credentials[1], credentials[2], credentials[4]

    # Get album info from form
    artist = request.form["artist"]
    album = request.form["album"]

    try:
        # Use the stored credentials
        network = pylast.LastFMNetwork(
            api_key=api_key,
            api_secret=api_secret,
            username=username,
            password_hash=pass_has
        )

        # Get album and tracks
        album_obj = network.get_album(artist, album)
        tracks = album_obj.get_tracks()

        # Scrobble all tracks with timestamps
        current_time = int(time.time())
        for i, track in enumerate(tracks):
            timestamp = current_time - (len(tracks) - i) * 30
            network.scrobble(
                artist=artist,
                title=track.title,
                album=album,
                timestamp=timestamp
            )

        return f"Success! Scrobbled {len(tracks)} tracks from '{album}' by {artist}"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)