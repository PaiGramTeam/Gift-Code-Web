from typing import List

from pydantic import BaseModel


class Code(BaseModel):
    code: str
    reward: List[str]
    expire: bool


class CodeList(BaseModel):
    main: List[Code]
    over: List[Code]
