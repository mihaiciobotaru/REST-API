CONTINUE = 100
OK = 200
CREATED = 201
NO_CONTENT = 204
MOVED_PERMANENTLY = 301
NOT_MODIFIED = 304
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
SERVICE_UNAVAILABLE = 503

EXCEPTED_STATUS_CODES = {
    'GET': [OK],
    'POST': [CREATED],
    'PUT': [OK],
    'DELETE': [OK],
    'OPTIONS': [OK]
}


def get_status_message(result_code):
    return {
        100: 'Continue',
        200: 'OK',
        201: 'Created',
        204: 'No Content',
        301: 'Moved Permanently',
        304: 'Not Modified',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        409: 'Conflict',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        503: 'Service Unavailable'
    }.get(result_code, 'Unknown')
