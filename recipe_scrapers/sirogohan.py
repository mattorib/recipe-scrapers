import re

from ._abstract import AbstractScraper
from ._exceptions import ElementNotFoundInHtml, StaticValueException
from ._grouping_utils import IngredientGroup
from ._utils import get_yields, normalize_string


class Sirogohan(AbstractScraper):
    @classmethod
    def host(cls):
        return "sirogohan.com"

    def author(self):
        raise StaticValueException(return_value="白ごはん.com")

    def site_name(self):
        raise StaticValueException(return_value="白ごはん.com")

    def total_time(self):
        time_element = self.soup.find("p", id="cooking-time")
        if time_element is None:
            raise ElementNotFoundInHtml("cooking-time")
        match = re.search(r"(\d+)", time_element.get_text())
        if match:
            return int(match.group(1))
        return None

    def yields(self):
        h2 = self.soup.select_one("section.material h2.material-ttl")
        if h2 is None:
            raise ElementNotFoundInHtml("material-ttl")
        return get_yields(h2.get_text())

    def ingredients(self):
        return [
            normalize_string(li.get_text())
            for li in self.soup.select("section.material li")
            if normalize_string(li.get_text())
        ]

    def ingredient_groups(self):
        label_map = {"a-list": "A", "b-list": "B", "c-list": "C"}
        groups = []
        for box in self.soup.select("section.material div.material-halfbox"):
            items = [
                normalize_string(li.get_text())
                for li in box.select("li")
                if normalize_string(li.get_text())
            ]
            if not items:
                continue
            ul = box.find("ul")
            classes = ul.get("class", []) if ul else []
            purpose = next(
                (label_map[c] for c in classes if c in label_map), None
            )
            groups.append(IngredientGroup(ingredients=items, purpose=purpose))
        return groups

    def category(self):
        return ",".join(
            normalize_string(li.get_text())
            for li in self.soup.select("ul.recipe-category li")
            if normalize_string(li.get_text())
        )

    def keywords(self):
        seen = set()
        result = []
        for a in self.soup.select("dl.recipe-keyword dd a"):
            text = normalize_string(a.get_text())
            if text and text not in seen:
                seen.add(text)
                result.append(text)
        return result

    def instructions(self):
        steps = []
        for block in self.soup.select("div.howto-block"):
            for p in block.select("p"):
                text = normalize_string(p.get_text())
                if text:
                    steps.append(text)
        return "\n".join(steps)
