# Last.fm Album Scrobbler

A web application that allows users to scrobble entire albums to Last.fm with a single click. Built with Flask, HTMX, and the Last.fm API, deployed to pythonanywhere @ [scrobbler.pythonanywhere.com](https://scrobbler.pythonanywhere.com/)

## Features

- **Secure Login System** - Users login with their Last.fm username and password
- **Credential Storage** - API credentials are securely stored in the database
- **Album Scrobbling** - Scrobble all tracks from an album automatically
- **Simple UI** - Clean, minimal interface for easy use

## How It Works

1. **Setup**: Users first set up their Last.fm API credentials
2. **Login**: Users authenticate with their username and password
3. **Scrobble**: Enter artist and album name to scrobble all tracks
4. **Automatic**: The app fetches the tracklist and scrobbles each song with proper timestamps

## Security Features
- Passwords are hased using MD5 before storage
- API credentials stored securely in the database
- No hardcoded credentials in the application
  
### Prerequisites

- Python 3.8+
- MySQL/MariaDB database
- Last.fm API account

### Last.fm API Setup

1. Visit [Last.fm API Applications](https://www.last.fm/api/account/create)
2. Create a new application
3. Copy your API Key and Shared Secret

### Dependencies
- **Flask** - Web framework
- **pylast** - Last.fm API client
- **DBcm**- Database connection management courtesy of Paul Barry
- **HTMX** - Dynamic frotend

### Deployment

The application is designed to work on PythonAnywhere but can be deployed on any WSGI-compatible hosting service. 
Visit [scrobbler.pythonanywhere.com](https://scrobbler.pythonanywhere.com/)


### Disclaimer
This application uses the [Last.fm](https://www.last.fm/home) API and must comply with their terms of service. Use responsibly and respect API rate limits.
