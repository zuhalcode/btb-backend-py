from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Any, List, Dict, Optional


class ResponseHandler:
    @staticmethod
    def success(data: Any, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "meta": {
                    "status": 200,
                    "message": message,
                },
                "data": data,
            },
        )

    @staticmethod
    def error(error: Exception, message: str) -> JSONResponse:
        if isinstance(error, ValidationError):
            # Pydantic validation error
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "meta": {
                        "status": 400,
                        "message": message,
                    },
                    "data": error.errors(),
                },
            )
        else:
            # General error
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "meta": {
                        "status": 500,
                        "message": message,
                    },
                    "data": str(error),
                },
            )

    @staticmethod
    def unauthorized(message: str = "unauthorized") -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "meta": {
                    "status": 403,
                    "message": message,
                },
                "data": None,
            },
        )

    @staticmethod
    def pagination(
        data: List[Any],
        pagination: Dict[str, int],
        message: str,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "meta": {
                    "status": 200,
                    "message": message,
                },
                "data": data,
                "pagination": pagination,
            },
        )

    @staticmethod
    def not_found(message: str = "not found") -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "meta": {
                    "status": 404,
                    "message": message,
                },
                "data": None,
            },
        )
