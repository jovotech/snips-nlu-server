from werkzeug.exceptions import HTTPException

class WrongFormatException(HTTPException):
    code = 422

class MissingParameterException(HTTPException):
    code = 400

class JovoModelSnipsException(HTTPException):
    code = 500

class MissingModelException(HTTPException):
    code = 400

class MissingResourceException(HTTPException):
    code = 500
