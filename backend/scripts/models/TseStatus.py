from models.BaseModel import BaseModel
from typing import Literal


class TseStatus(BaseModel):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    # Share the Current TSE Status
    # Operations are Possible During Ok & Warning
    # Warnings SHALL NOT be ignored as they are more on the Urgent side to prevent serve issues
    # Stop Prevents Operation, May be caused by Events that will Pass, or more Serve Situations
    # that might require Replacements
    # The reason String SHALL be used for Warning & Stop to provide a Compound Explanation for this Current Status
    # The reason String MAY be Multiline, different Reasons MUST be separated in Lines
    def __init__(self, generalStatus: Literal["Ok", "Warning", "Stop"], reason: str):
        self.status = generalStatus
        self.reason = reason
