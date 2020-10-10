from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    """
    Custom exception handler if decided to create own format
    of error responses
    """

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response
