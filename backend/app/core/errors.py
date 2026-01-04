from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class BusinessError(Exception):
    code: str
    message: str
    details: dict | None
    status_code: int

    def __init__(
        self,
        code: str,
        message: str,
        details: dict | None = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code


def raise_business_error(
    code: str,
    message: str,
    details: dict | None = None,
    status_code: int = 400,
) -> None:
    raise BusinessError(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
    )


def to_error_response(code: str, message: str, details: dict | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }
