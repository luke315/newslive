from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from Newslive.utils.logging import logger
from Newslive.utils.response import APIResponse


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        logger.error('%s - %s - %s' % (context['view'], context['request'].method, exc))
        return APIResponse(3, '异常',
            results={'detail': '服务器错误'},
           http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
           exception=True
        )
    return APIResponse(3, '异常', results=response.data, http_status=status.HTTP_401_UNAUTHORIZED)

