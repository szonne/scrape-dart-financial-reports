import logging
import os
from io import BytesIO
from xml.etree.ElementTree import parse
from zipfile import ZipFile

import requests
from pydash import py_

from utils import get_api_key
from config import BASE_URL

API_KEY = get_api_key()

class Corp:
    def __init__(self, api_key=API_KEY):
        if not api_key:
            raise ValueError('API key is not valid')
        self.api_key = api_key

    def get_list(self):
        if not (
            "corpCode" in os.listdir(".") and "CORPCODE.xml" in os.listdir("corpCode")
        ):
            target_url = f"{BASE_URL}/corpCode.xml"
            res = requests.get(target_url, params={"crtfc_key": self.api_key})

            with ZipFile(BytesIO(res.content)) as zipfile:
                zipfile.extractall("corpCode")

        xml_tree = parse("corpCode/CORPCODE.xml")
        root = xml_tree.getroot()
        corp_list = []
        for item in root.findall("list"):
            corp_list.append(
                {
                    "corp_code": item.findtext("corp_code"),
                    "corp_name": item.findtext("corp_name"),
                    "stock_code": item.findtext("stock_code"),
                    "modify_date": item.findtext("modify_date"),
                }
            )

        corp_list = py_.filter(corp_list, lambda val: val["stock_code"] != " ")

        # Remove irrevalent values
        corp_list = py_.filter(corp_list, lambda val: "스팩" not in val["corp_name"])
        corp_list = py_.filter(corp_list, lambda val: "펀드" not in val["corp_name"])
        corp_list = py_.filter(
            corp_list, lambda val: "자원개발" not in val["corp_name"]
        )
        corp_list = py_.filter(
            corp_list, lambda val: "유한공사" not in val["corp_name"]
        )
        corp_list = py_.filter(
            corp_list, lambda val: "기업인수목적" not in val["corp_name"]
        )
        corp_list = py_.filter(
            corp_list, lambda val: "투자회사" not in val["corp_name"]
        )
        corp_list = py_.filter(
            corp_list, lambda val: not val["corp_name"].endswith("리츠")
        )

        return corp_list

    def find_by_name(self, name, corp_list=None):
        if not corp_list:
            corp_list = self.get_list()

        target_corp = py_.find(corp_list, lambda val: val["corp_name"] == name)

        if not target_corp:
            logging.warning(f"There is no corp of which name is {name}")
            return None

        return target_corp

    def find_by_code(self, code, corp_list=None):
        if not corp_list:
            corp_list = self.get_list()

        target_corp = py_.find(corp_list, lambda val: val["corp_code"] == code)
        if not target_corp:
            logging.warning(f"There is no corp of which code is {code}")
            return None

        return target_corp
