from enum import Enum

from django.http import JsonResponse


class ResponseCode(Enum):
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


def api_response(code, msg, data=None):
    status_code = code.value if isinstance(code, ResponseCode) else int(code)
    return JsonResponse(
        {
            "code": status_code,
            "msg": msg,
            "data": data,
        },
        status=status_code,
        safe=False,
    )
