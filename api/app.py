from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

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
    # and we add a relationship so we can reference the parent psalm directly
    psalm = db.relationship('Psalm', backref=db.backref('stanzas', lazy=True))

##############################################################################
##############################################################################
#######  STEP THREE: MAKING THE ROUTES AND FUNCTIONS TO SERVE THE JSON #######
##############################################################################

# let's define a route to return all psalms, or a filtered set based on length
# i.e., with a query parameter ?stanzas=[n] where n is a list of ints
@app.route('/api/psalms', methods=['GET'], strict_slashes=False)
def list_psalms():
    # we'll start defining our query (we'll start big and narrow it)
    query = Psalm.query
    # let's look for filters
    requested_stanzas = request.args.getlist('stanzas')
    # and apply them to the query if they exist, to narrow down the query
    if requested_stanzas:
        query = query.filter(Psalm.Stanzas.in_(requested_stanzas))
    # now we will actually execute the query and format and return some JSON
    psalms_to_return = query.all()
    psalms_data = [{"number": p.Number,
                    "title": p.Title,
                    "subtitle": p.Subtitle,
                    "meter": p.Meter,
                    "stanzas": p.Stanzas,
                    "audio": p.Audio,
                    "text": p.PsalmText
                    } for p in psalms_to_return]
    return jsonify(psalms_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
