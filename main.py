from typing import List

from models.code import CodeList, Code
from models.honkai import get_code

from pathlib import Path

data_path = Path("data")
custom_path = data_path / "custom.json"
code_path = data_path / "code.json"


def merge_code(over: List[Code], custom: CodeList) -> CodeList:
    over_codes = [i for i in over]
    custom_over_codes = [i.code for i in custom.over]
    for code in over_codes:
        if code.code in custom_over_codes:
            continue
        custom.over.append(code)
    return custom


def main():
    over = get_code()
    with open(custom_path, "r", encoding="utf-8") as f:
        custom = CodeList.parse_raw(f.read())
    custom = merge_code(over, custom)
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(custom.json(indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
