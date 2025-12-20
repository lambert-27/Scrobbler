from flask import Flask, render_template, request, session, redirect, url_for
import secrets
import bcrypt
from model import DatabaseModel, LastFMModel

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

app = Flask(__name__)
# Start a session for user using secrets module
app.secret_key =  secrets.token_hex(32)

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

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if DatabaseModel.verify_login(username, password):
        session['username'] = username
        return redirect(url_for('scrobble_page'))  # Redirect user scrobble instantly!
    else:
        return render_template("login.html", 
                             the_title="Login",
                             error="Invalid username or password.")


#app.get to redirect to scrobble url if logged in
@app.get("/scrobble")
def scrobble_page():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('opening_page'))  # Redirect to login page
    
    return render_template("scrobble.html", 
                          the_title="Scrobble Album", 
                          username=session['username'])
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
    DatabaseModel.save_credentials(api_key, api_secret, username, password)

    return "Credentials saved! You can now login to scrobble albums."

@app.post("/scrobble")
def scrobble_album():
    # Check if user is logged in
    if 'username' not in session:
        return "Error: Please login first."

    username = session['username']

    # Get credentials from database
    credentials = DatabaseModel.get_credentials_by_username(username)
    if not credentials:
        return "Error: No credentials found for your account. Please set up credentials first."

    # credentials tuple: (id, api_key, api_secret, username, pass_has)
    api_key, api_secret, pass_has = credentials[1], credentials[2], credentials[4]

    # Get album info from form
    artist = request.form["artist"]
    album = request.form["album"]

    try:
        lastfm = LastFMModel(api_key, api_secret, username, pass_has)
        tracks_count = lastfm.scrobble_album(artist, album)
        
        return f"Success! Scrobbled {tracks_count} tracks from '{album}' by {artist}"

    except Exception as e:
        return f"Error: Could not scrobble album. Please check you input the correct Artist/Album"

if __name__ == "__main__":
    app.run(debug=True)