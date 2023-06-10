from typing import List

from pydantic import BaseModel


class Reward(BaseModel):
    name: str
    cnt: int


class Code(BaseModel):
    code: str
    reward: List[Reward]
    expire: int


class CodeList(BaseModel):
    main: List[Code]
    over: List[Code]
