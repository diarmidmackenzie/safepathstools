# A module that can be used/edited to write out data directly, rather than using Flask / URL.
# For this to work, you need to comment out a few lines in views.py before importing.
#
# from . import app
# from flask import request
# @app.route('/')
# @app.route('/infection-data')
#
# Yes this is a hack & should be tidied up somehow!

import views

text = views.write_cursor_file(1,
					           1,
					           12.1,
					           14.1,
					           "Test Health Authority",
					           2,
					           12,
					           10)

print(text)
