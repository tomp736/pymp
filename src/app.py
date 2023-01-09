
from flask import Flask
import os
import logging

from routes import base, video, thumb, extensions

app = Flask(__name__)
app.register_blueprint(extensions.app_def)
app.register_blueprint(video.app_video)
app.register_blueprint(thumb.app_thumb)
app.register_blueprint(base.app_base)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'), 
        port=int(os.environ.get('FLASK_RUN_PORT', '0')), 
        debug=False
        )