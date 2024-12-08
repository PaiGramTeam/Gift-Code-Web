import re
from pytz import timezone
from datetime import datetime
from typing import List

from httpx import get
from bs4 import BeautifulSoup, Tag
from .code import Code, Reward


url = "https://honkai.gg/codes/"
reward_map = {
    "Stellar Jade": "星琼",
    "Credit": "信用点",
    "Credits": "信用点",
    "Traveler's Guide": "漫游指南",
    "Traveler’s Guide": "漫游指南",
    "Refined Aether": "提纯以太",
    "Adventure Log": "冒险记录",
    "Dust of Alacrity": "疾速粉尘",
    "Condensed Aether": "凝缩以太",
    "Cosmic Fried Rice": "大宇宙炒饭",
    "Travel Encounters": "旅情见闻",
    "Energy Drink": "能量饮料",
    "Startaro Bubble": "星芋啵啵",
    "Lost Gold Fragments": "遗失碎金",
    "Hypnotic Hammer": "安眠锤",
    "Camo Paint": "迷彩油漆",
    "Dry Emergency Light": "干制应急灯",
    "Flaming Potent Tea": "烈焰浓茶",
    "Steamed Puffergoat Milk": "热浮羊奶",
    "Bottled Soda": "罐装快乐水",
    "All or Nothing": "孤注一掷",
    "“Sour Dreams” Soft Candy": "「酸梦」牌软糖",
    "High-Tech Protective Gear": "科技护具",
    "Sweet Dreams Soda": "好梦气泡饮",
    "“Dreamlight” Mixed Sweets": "「彩梦」什锦糖果",
}


def parse_reward(reward: List[str]) -> Reward:
    try:
        name = reward_map.get(reward[0])
        if not name:
            # 判断是否为中文
            if not re.search("[\u4e00-\u9fa5]", reward[0]):
                print("Unknown reward: ", reward[0])
            name = reward[0]
        cnt = int(reward[1].replace(",", ""))
        return Reward(
            name=name,
            cnt=cnt,
        )
    except Exception as e:
        print("Bad reward data: ", reward)
        raise e


def parse_code(tr: Tag) -> Code:
    tds = tr.find_all("td")
    code = tds[0].text.strip()
    try:
        data = str(tds[2]).split("<br/>")
        expire = data[1]
    except (IndexError, TypeError):
        _, expire = datetime(1970, 1, 1, 1, 0, 0, 0), datetime(2099, 12, 31, 23, 59, 59, 999999)
    if isinstance(expire, str):
        try:
            expire = expire.split(": ")[1].replace("</td>", "").replace("<td>", "")
            if "Unknown" in expire:
                expire = datetime(2099, 12, 31, 23, 59, 59, 999999)
            elif "Expired" in expire:
                expire = datetime(1970, 1, 1, 1, 0, 0, 0)
            elif "," in expire:
                expire = datetime.strptime(expire, "%B %d, %Y")
            else:
                expire = datetime.strptime(expire, "%B %d")
                expire = expire.replace(year=datetime.now().year)
        except IndexError:
            expire = datetime(2099, 12, 31, 23, 59, 59, 999999)
    expire = timezone("Asia/Shanghai").localize(expire)
    expire = int(expire.timestamp() * 1000)
    rewards = []
    for reward in str(tds[1]).split("<br/>"):
        reward_soup = BeautifulSoup(reward, "lxml")
        reward_text = " ".join(reward_soup.text.strip().split()).replace("×", "x")
        reward_div = []
        if " x " in reward_text:
            reward_div = reward_text.split(" x ")
        elif " x" in reward_text:
            reward_div = reward_text.split(" x")
        if len(reward_div) < 2:
            print("Bad td data: ", tds[1])
            continue
        parsed_reward = parse_reward(reward_div)
        if parsed_reward:
            rewards.append(parsed_reward)
    if not rewards:
        for reward in tds[1].find_all("a"):
            reward_a = reward.text.strip().split(" x ")
            if len(reward_a) < 2:
                print("Bad a data: ", tds[1])
                continue
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
            if not tr.text:
                continue
            codes.append(parse_code(tr))
    codes.sort(key=lambda x: x.expire, reverse=True)
    return codes
