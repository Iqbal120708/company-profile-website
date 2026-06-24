# middleware.py

import logging

logger = logging.getLogger("request_logger")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code >= 400:
            logger.warning(
                "%s %s -> %s",
                request.method,
                request.path,
                response.status_code
            )

        return response
