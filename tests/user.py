from datetime import datetime

from pydantic import Field
from pydastic import ESModel
from typing import Optional

class User(ESModel):

    name: str
    phone: Optional[str]
    last_login: datetime = Field(default_factory=datetime.now)

    class Meta:
        index = "user"
