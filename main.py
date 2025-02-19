import json

from models.code import CodeList
from models.rockpapershotgun import get_code

from pathlib import Path

data_path = Path("data")
code_path = data_path / "code.json"


def main():
    over = get_code()
    if not over:
        raise ValueError("Get code failed")
    custom = CodeList(main=[], over=over)
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(custom.model_dump(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
