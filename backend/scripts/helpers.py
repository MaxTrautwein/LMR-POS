# Parse Json to List of BaseModel Descendant
# Currently used Basket when making a Sale
from functools import wraps
from typing import TypeVar

from flask import jsonify

from models import BaseModel


T = TypeVar('T', bound='BaseModel')


def jsonToListOfModel(json: list[dict], model_class: T) -> list[T]:
    return [model_class(**data) for data in json]


# Wrapper Function, so that we can Return Classes defiled in models
# Each Model is a Child of BaseModel, allowing us to easily convert them to a Dict
def jsonify_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, BaseModel.BaseModel):
            return jsonify(result.to_dict())
        return result

    return wrapper
