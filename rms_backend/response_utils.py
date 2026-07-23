from rest_framework.response import Response
from rest_framework import status


def response_success(message="Success", data=None):
    """
    Standard response for successful requests.

    :param message: The success message to include in the response body.
    :param data: The data to include in the response body.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data
        },
        status=status.HTTP_200_OK
    )


def response_created(message="Created successfully", data=None):
    """
    Standard response for resource creation requests.

    :param message: The success message to include in the response body.
    :param data: The created resource data.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data
        },
        status=status.HTTP_201_CREATED
    )


def response_bad_request(message="Bad request", data=None):
    """
    Standard response for bad request errors.

    :param message: The error message to include in the response body.
    :param data: Validation errors or additional information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_400_BAD_REQUEST
    )


def response_unauthorized(message="Unauthorized", data=None):
    """
    Standard response for unauthorized requests.

    :param message: The error message to include in the response body.
    :param data: Additional error information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_401_UNAUTHORIZED
    )


def response_forbidden(message="Forbidden", data=None):
    """
    Standard response for forbidden requests.

    :param message: The error message to include in the response body.
    :param data: Additional error information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_403_FORBIDDEN
    )


def response_not_found(message="Not found", data=None):
    """
    Standard response for resource not found requests.

    :param message: The error message to include in the response body.
    :param data: Additional error information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_404_NOT_FOUND
    )


def response_conflict(message="Conflict", data=None):
    """
    Standard response for conflict requests.

    :param message: The error message to include in the response body.
    :param data: Additional error information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_409_CONFLICT
    )


def response_server_error(message="Internal server error", data=None):
    """
    Standard response for internal server errors.

    :param message: The error message to include in the response body.
    :param data: Additional error information.
    :return: A DRF Response object.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": data
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )