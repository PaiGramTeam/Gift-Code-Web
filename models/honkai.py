from datetime import datetime
from typing import List

from httpx import get
from bs4 import BeautifulSoup, Tag
from .code import Code, Reward


url = "https://honkai.gg/cn/codes"
reward_map = {
    "Stellar Jade": "星琼",
    "Credit": "信用点",
    "Credits": "信用点",
    "Traveler's Guide": "漫游指南",
    "Refined Aether": "提纯以太",
    "Adventure Log": "冒险记录",
    "Dust of Alacrity": "疾速粉尘",
    "Condensed Aether": "凝缩以太",
    "Cosmic Fried Rice": "大宇宙炒饭",
}


def parse_reward(reward: List[str]) -> Reward:
    try:
        name = reward_map.get(reward[0])
        if not name:
            print("Unknown reward: ", reward[0])
            name = reward[0]
        return Reward(
            name=name,
            cnt=int(reward[1]),
        )
    except ValueError:
        print("Bad reward data: ", reward)


def parse_code(tr: Tag) -> Code:
    tds = tr.find_all("td")
    code = tds[0].text.strip()
    expire = tds[2].text.strip()
    if expire.endswith("?"):
        expire = datetime(2099, 12, 31, 23, 59, 59, 999999)
    else:
        expires = expire.split(" - ")
        day = expires[1].split(" ")[-1]
        month = expires[0].split(" ")[0]
        try:
            if " " not in expires[1]:
                raise ValueError
            month = expires[1].split(" ")[0]
        except ValueError:
            pass
        now = datetime.now()
        expire = datetime.strptime(f"{day} {month}", "%d %b")
        expire = expire.replace(year=now.year, hour=23, minute=59, second=59, microsecond=999999)
    expire = int(expire.timestamp() * 1000)
    rewards = []
    for reward in tds[1].find_all("div", {"class": "flex"}):
        reward_div = reward.text.strip().split("\xa0x ")
        parsed_reward = parse_reward(reward_div)
        if parsed_reward:
            rewards.append(parsed_reward)
    for reward in tds[1].find_all("a"):
        reward_a = reward.text.strip().split(" x ")
        parsed_reward = parse_reward(reward_a)
        if parsed_reward:
            rewards.append(parsed_reward)
    return Code(code=code, reward=rewards, expire=expire)


def get_code():
    html = get(url).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    codes = []
    for table in tables:
        trs = table.find_all("tr")[1:]
        for tr in trs:
            codes.append(parse_code(tr))
    codes.sort(key=lambda x: x.expire, reverse=True)
    return codes
