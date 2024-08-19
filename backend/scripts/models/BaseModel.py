

# BaseModel
class BaseModel:
    def to_dict(self):
        # Convert all attributes to a serializable format
        return {key: self._convert_value(value) for key, value in self.__dict__.items()}

    @staticmethod
    def _convert_value(value):
        if isinstance(value, list):
            # Convert each item in the list, especially handling BaseModel instances
            return [BaseModel._convert_value(item) for item in value]
        elif isinstance(value, BaseModel):
            return value.to_dict()  # Convert nested BaseModel instances
        else:
            return value