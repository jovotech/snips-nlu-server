from werkzeug.exceptions import HTTPException

class WrongFormatException(HTTPException):
    code = 422

class MissingParameterException(HTTPException):
    code = 400
