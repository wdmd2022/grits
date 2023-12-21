from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
import json
from flask_redis import FlaskRedis
from functools import wraps

##############################################################################
######################### let's serve up an API! #############################
##############################################################################
## We'll set up the server with Flask, #######################################
## Use Flask-SQLAlchemy to connect to our MySQL DB, ##########################
## And serve up results in JSON ##############################################
##############################################################################


##############################################################################
##############################################################################
#################### STEP ONE: INITIALIZING FLASK APP ########################
##############################################################################
app = Flask(__name__)
CORS(app)
app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = FlaskRedis(app)

##############################################################################
##############################################################################
############### STEP TWO: CONNECTING TO MYSQL ################################
##############################################################################
# first we make the connection
alc_dialect_driver = 'mysql+mysqlconnector'
alc_user = os.environ['MYSQL_USER']
alc_pass = os.environ['MYSQL_PASSWORD']
alc_host = os.environ['MYSQL_HOST']
alc_db = os.environ['MYSQL_DATABASE']
alc_uri = f"{alc_dialect_driver}://{alc_user}:{alc_pass}@{alc_host}/{alc_db}"
# and using these strings we can configure our Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = alc_uri
# and finally intialize that database connection
db = SQLAlchemy(app)

# now we can develop a model to manipulate our records as python objects.
class Psalm(db.Model):
    __tablename__ = 'psalms'
    Number = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255))
    Subtitle = db.Column(db.String(255))
    Meter = db.Column(db.String(50))
    PsalmText = db.Column(db.Text)
    Stanzas = db.Column(db.Integer)
    Audio = db.Column(db.String(255))

class Stanza(db.Model):
    __tablename__ = 'stanzas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PsalmNumber = db.Column(db.Integer, db.ForeignKey('psalms.Number'))
    StanzaNumber = db.Column(db.Integer)
    Meter = db.Column(db.String(50))
    StanzaText = db.Column(db.Text)
    Timestamp = db.Column(db.String(12))
    # and we add a relationship so we can reference the parent psalm directly
    psalm = db.relationship('Psalm', backref=db.backref('stanzas', lazy=True))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)

##############################################################################
##############################################################################
#######  STEP THREE: MAKING THE ROUTES AND FUNCTIONS TO SERVE THE JSON #######
##############################################################################

# first, let's make a decorator that will require an API key for those accessing
# our service.
def require_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key_header = request.headers.get('X-API-KEY')
        api_key_url_param = request.args.get('api_key')
        api_key = api_key_header or api_key_url_param
        # is it in the database though?
        user = User.query.filter_by(api_key=api_key).first()
        if user is None:
            return jsonify({"error": "You need a present and valid API key, nice try"}), 404
        return f(*args, **kwargs)
    return decorated_function

# and let's make a route that will validate our users
@app.route('/api/validate-user', methods=['POST'], strict_slashes=False)
def validate_user():
    data = request.get_json()
    username = data.get('username')
    api_key = data.get('api_key')
    user = User.query.filter_by(username=username, api_key=api_key).first()
    if user:
        return jsonify({'valid': True, 'api_key': api_key})
    else:
        return jsonify({'valid': False}), 401

# ALL PSALMS (filterable, paginate-able)
# let's define a route to return all psalms, or a filtered set based on length
# i.e., with a query parameter ?stanzas=[n] where n is a list of ints
# pagination is available through per_page= and page= query parameters
@app.route('/api/psalms', methods=['GET'], strict_slashes=False)
@require_key
def list_psalms():
    # first we'll check Redis for a unique cache key based on the query parameters
    cache_key = f"psalms_data_{request.query_string.decode('utf-8')}"
    # we'll see if it's possible to grab data from Redis based on the cache_key
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    # BUT, IF NOT IN REDIS, WE WILL GET IT THE OLD-FASHIONED WAY
    # we'll start defining our query (we'll start big and narrow it)
    query = Psalm.query
    # let's look for number-of-stanza based filters
    requested_stanzas = request.args.getlist('stanzas')
    # and apply them to the query if they exist, to narrow down the query
    if requested_stanzas:
        query = query.filter(Psalm.Stanzas.in_(requested_stanzas))
    # then let's look for pagination query parameters
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)
    # and apply them only if they both exist
    if page is not None and per_page is not None:
        paginated_psalms = query.paginate(page=page, per_page=per_page, error_out=False)
        psalms_to_return = paginated_psalms.items
    else:
        psalms_to_return = query.all()
    # now we will format and return some JSON
    psalms_data = [{"number": p.Number,
                    "title": p.Title,
                    "subtitle": p.Subtitle,
                    "meter": p.Meter,
                    "stanzas": p.Stanzas,
                    "audio": p.Audio,
                    "text": p.PsalmText
                    } for p in psalms_to_return]
    redis_client.setex(cache_key, 3600, json.dumps(psalms_data))
    return jsonify(psalms_data)

# ONE PSALM
# now let's make a route to return a single specific psalm
@app.route('/api/psalms/<int:psalm_number>', methods=['GET'], strict_slashes=False)
@require_key
def get_psalm(psalm_number):
    # request it from the database
    requested_psalm = Psalm.query.get(psalm_number)
    if requested_psalm is None:
        return jsonify({"error": "Please pick a number from 1 to 150"}), 404
    psalm_data = {"number": requested_psalm.Number,
                    "title": requested_psalm.Title,
                    "subtitle": requested_psalm.Subtitle,
                    "meter": requested_psalm.Meter,
                    "stanzas": requested_psalm.Stanzas,
                    "audio": requested_psalm.Audio,
                    "text": requested_psalm.PsalmText
    }
    return jsonify(psalm_data)

# ONE STANZA
# now let's make a route to return a specific stanza from a psalm
@app.route('/api/psalms/<int:psalm_number>/stanza/<int:stanza_number>', methods=['GET'], strict_slashes=False)
@require_key
def get_stanza(psalm_number, stanza_number):
    # request it from the database
    requested_stanza = Stanza.query.filter_by(PsalmNumber=psalm_number, StanzaNumber=stanza_number).first()
    if requested_stanza is None:
        return jsonify({"error": "I implore you to pick a stanza that exists"}), 404
    stanza_data = {
        "psalm_number": requested_stanza.PsalmNumber,
        "stanza_number": requested_stanza.StanzaNumber,
        "num_stanzas_in_psalm": requested_stanza.psalm.Stanzas if requested_stanza.psalm else 0,
        "meter": requested_stanza.Meter,
        "timestamp": requested_stanza.Timestamp,
        "stanza_text": requested_stanza.StanzaText
    }
    return jsonify(stanza_data)

# ALL STANZAS
# and also a route to return an array of all stanzas associated with a psalm
@app.route('/api/psalms/<int:psalm_number>/stanzas', methods=['GET'], strict_slashes=False)
@require_key
def get_stanzas(psalm_number):
    stanzas = Stanza.query.filter_by(PsalmNumber=psalm_number).all()
    if not stanzas:
        return jsonify({'error': f'Next time try picking a psalm number between 1-150'}), 404
    stanza_data = [{
        'psalm_number': stanza.PsalmNumber,
        'stanza_number': stanza.StanzaNumber,
        'meter': stanza.Meter,
        'stanza_text': stanza.StanzaText,
        'num_stanzas_in_psalm': stanza.psalm.Stanzas if stanza.psalm else 0,
        'timestamp': stanza.Timestamp
    } for stanza in stanzas]
    return jsonify(stanza_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
