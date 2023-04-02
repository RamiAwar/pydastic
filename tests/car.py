from datetime import datetime
from typing import Optional

from pydantic import Field

from pydastic import ESAsyncModel


class Car(ESAsyncModel):
    model: str
    year: Optional[int]
    last_test: datetime = Field(default_factory=datetime.now)

    class Meta:
        index = "car"
