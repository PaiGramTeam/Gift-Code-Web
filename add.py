from pathlib import Path
from sys import argv
from datetime import datetime
from typing import List

from models.code import CodeList, Code, Reward

data_path = Path("data")
custom_path = data_path / "custom.json"


def add(code: str, expire_str: str, rewards_str: List[str]) -> Code:
    if ":" in expire_str:
        expire = datetime.strptime(expire_str, "%Y-%m-%d:%H:%M:%S")
        expire = expire.replace(microsecond=999999)
    else:
        expire = datetime.strptime(expire_str, "%Y-%m-%d")
        expire = expire.replace(hour=23, minute=59, second=59, microsecond=999999)
    rewards = []
    for reward_str in rewards_str:
        reward_list = reward_str.split(":")
        rewards.append(
            Reward(
                name=reward_list[0],
                cnt=int(reward_list[1])
            )
        )
    return Code(
        code=code,
        expire=int(expire.timestamp() * 1000),
        reward=rewards,
    )


if __name__ == '__main__':
    try:
        add_type = argv[1]
        if add_type not in ["main", "over"]:
            raise IndexError
        code = add(argv[2], argv[3], argv[4:])
        with open(custom_path, "r", encoding="utf-8") as f:
            custom: CodeList = CodeList.parse_raw(f.read())
        if add_type == "main":
            main_codes = [i.code for i in custom.main]
            if code.code in main_codes:
                raise ValueError("Duplicate code")
            custom.main.append(code)
        else:
            over_codes = [i.code for i in custom.over]
            if code.code in over_codes:
                raise ValueError("Duplicate code")
            custom.over.append(code)
        custom.main.sort(key=lambda x: x.expire, reverse=True)
        custom.over.sort(key=lambda x: x.expire, reverse=True)
        with open(custom_path, "w", encoding="utf-8") as f:
            f.write(custom.json(indent=4, ensure_ascii=False))
    except IndexError:
        print("Usage: python add.py [main/over] [code] [expire] [rewards...]")
        print("Example: python add.py main code 2023-11-1 星琼:1 信用点:1000")
