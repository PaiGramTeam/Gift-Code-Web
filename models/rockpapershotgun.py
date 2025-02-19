from httpx import get
from bs4 import BeautifulSoup, Tag
from .code import Code


url = "https://www.rockpapershotgun.com/honkai-star-rail-codes-list"


def parse_code(tr: Tag) -> Code:
    tds = tr.find_all("td")
    code = tds[0].text.strip()
    rewards = [i.strip() for i in tds[1].text.strip().split(";")]
    expire = tds[2].text.strip() == "Expired"
    return Code(code=code, reward=rewards, expire=expire)


def get_code():
    html = get(url).text
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    codes = []
    trs = table.find_all("tr")[1:]
    for tr in trs:
        if not tr.text:
            continue
        codes.append(parse_code(tr))
    return codes
