# API documentation:

## Important Notes
*all* requests require an API key sent either:
- in the header as ‘X-API-KEY’
- as a url parameter: ?api_key={key}
### Test api_key is: t3stk3y1337 (if using frontend, use with username llcooldoug)

##### Pagination can be accomplished using the following url parameters:
- ?per_page=INT
- ?page=INT
Both parameters must be used to impact the results returned.

## GET A LIST OF PSALMS
localhost:5000/api/psalms, Methods: GET
returns a list of psalms, in the JSON format:
                   {"number": _____,
                    "title": ______,
                    "subtitle": _____,
                    "meter": ______,
                    "stanzas": ___,
                    "audio": _____,
                    "text": ____
                     }

## GET A SINGLE PSALM
localhost:5000/api/psalms/<int:psalm_number>, Methods: GET
returns a single psalm, in the JSON format:
                   {"number": _____,
                    "title": ______,
                    "subtitle": _____,
                    "meter": ______,
                    "stanzas": ___,
                    "audio": _____,
                    "text": ____
                     }

## GET A SINGLE STANZA
localhost:5000/api/psalms/<int:psalm_number>/stanza/<int:stanza_number>, Methods: GET
returns a single stanza, in the JSON format:
       {“psalm_number": ___,
        "stanza_number": ___,
        "num_stanzas_in_psalm": ___,
        "meter": ______,
        "timestamp": ____,
        "stanza_text": _____
        }

## GET ALL STANZAS
localhost:5000/api/psalms/<int:psalm_number>/stanzas, Methods: GET
returns all stanzas of a given psalm, in a list where they are each in the JSON format:
       {“psalm_number": ___,
        "stanza_number": ___,
        "num_stanzas_in_psalm": ___,
        "meter": ______,
        "timestamp": ____,
        "stanza_text": _____
        }

## USER VALIDATIONlocalhost:5000/api/validate-user, Methods: POST
returns a JSON object with values based on the ‘username’ and ‘api_key’ from the JSON body of the request.
- if user is valid, response is JSON object with body:{‘valid’: True, ‘api_key’: ______}
- if user is not valid, response is JSON object with body:
	{‘valid’: False}
