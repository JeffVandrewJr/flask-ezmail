# Flask-EZMail

(c) 2019 Jeff Vandrew Jr

Flask-EZMail is easier email for Flask. 

Flask-EZMail is a fork of Flask-Mail. it maintains high compatibility with Flask-Mail, such that very little code refactoring is needed to switch from one to the other.

Flask-Mail is a convenient wrapper for smtlib, but it requrires that SMTP settings be loaded on app creation. With Flask-Mail, if your user is entering SMTP settings after app creation (which would be the case if the SMTP settings are set via a web-based administrator interface while the app is running), it's not optimal and requires workarounds.

That's where Flask-EZMail comes in. Flask-EZMail is designed to be flexible. You can load SMTP settings at app creation like you would with Flask-Mail, or you can load them at any later time if your user is setting them through an web admin panel. Check out the examples below.

## Installation
```bash
pip install flask-ezmail
```

## Creating an Email Object

Let's say you want to load SMTP settings at app creation and never change them, just like Flask-Mail would expect:
```python3
# app/__init__.py
...
from flask_ezmail import Mail
...

<other app creation stuff goes here>

mail = Mail(
  server=app.config['MAIL_SERVER'],
  username=app.config['MAIL_USERNAME'],
  password=app.config['MAIL_PASSWORD'],
  port=app.config['MAIL_PORT'],
  use_tls=True,
  default_sender=app.config['DEFAULT_SENDER'],
  debug=app.debug
)
```

In that example, you'd have a global variable called `mail` that you'd be able to import in your other modules using `from app import mail`. There's nothing special there, as that's similar to Flask-Mail. 

But now instead assume your user fills out a form in the admin panel that sets SMTP settings later, after app creation. This example will assume you've defined that form for getting SMTP data as `EmailSetupForm` in `app.forms`. You could then set up mail this way instead:

```python3
from app.forms import EmailSetupForm
from flask_ezmail import Mail

@app.route('/emailsetup', methods=[GET, POST])
def email_setup():
  form = EmailSetupForm()
  
  <code to render the form, accept POST data, etc>

  #create mail object using data from the form
  mail = Mail(
    server=form.server.data,
    username=form.username.data,
    password=form.password.data,
    port=form.port.data,
    use_tls=True,
    default_sender=form.default_sender.data,
    debug=False
  )
```
You now have a mail object created on the fly! You'll probably want to stash it for later use elsewhere in your app. You have lots of options regarding how to do that:

1. You could pickle it and save it to redis:
```python3
import pickle

# this assumes you've set up redis in app/__init__.py
current_app.redis.set('mail', pickle.dumps(mail))
```
Alternatively if you're using Flask-SQLAlchemy, you could create an email model that inherits from `Mail`, and save the mail object in your database instead:
```python3
# app/models.py

from flask_ezmail import Mail

class Email(Mail, db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(128))
    port = db.Column(db.Integer)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))
    default_sender = db.Column(db.String(128))
    outgoing_email = db.Column(db.String(128))
    use_tls = db.Column(db.Boolean)
    use_ssl = db.Column(db.Boolean)
    debug = db.Column(db.Boolean, default=False)
    max_emails = db.Column(db.Integer)
    suppress = db.Column(db.Boolean)
```
If you went the SQLAlchemy route, any time you need to grab your email client you'd just:
```python3
mail = Email.query.first()
```
And if you needed to change an SMTP setting on the fly:
```python3
from app import db
from app.models import Email

mail = Email.query.first()
if mail is not None:
    mail.server = 'example.net'
    db.session.commit()
```

## Sending an Email
Sending a message uses the same Message object as Flask-Mail (cloned in Flask-EZMail).
```python3
from flask_ezmail import Message

msg = Message(
    'Test Message',
    sender='sender@sender.com',
    recipients=['recipient@recipient.com'],
)
mail.send(msg)
```
Flask-EZmail likewise uses the same `connect()` method as Flask-Mail for bulk emails.
