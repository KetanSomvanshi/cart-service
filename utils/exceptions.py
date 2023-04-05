# if custom exception is being used from celery , make sure init takes only one arguement
import json


class AppException(Exception):
    def __init__(self, status_code: int = 500, message: str = None):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return (
            json.dumps({"exception_name": str(self.__class__.__name__),
                        "exception_msg": self.message,
                        "exception_status_code": self.status_code})
        )
