from flask_login import login_required, current_user
from flask import render_template, session
from models import *
from config import *
from routes.login import *
from routes.products import *
from routes.customers import *
from routes.logs import *
from functions import *

'''
 _________________
< Web Application >
 -----------------
   \
    \
     \
        __ \ / __
       /  \ | /  \
           \|/
       _.---v---.,_
      /            \  /\__/\
     /              \ \_  _/
     |__ @           |_/ /
      _/                /
      \       \__,     /
   ~~~~\~~~~~~~~~~~~~~`~~~
'''
# Home Page + Profile Page
@app.route('/')
def index():
    if current_user.is_authenticated:
        session['name'] = current_user.name
    else:
        session['name'] = ''
    return render_template('index.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

if __name__ == '__main__':
    app.run(debug=True)