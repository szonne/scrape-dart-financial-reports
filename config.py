from enum import Enum
from typing import TypedDict, List


BASE_URL = "https://opendart.fss.or.kr/api"


class ReportCodes(Enum):
    Q1 = "11013"
    Q2 = "11012"
    Q3 = "11014"
    Q4 = "11011"


class AccountDetail(TypedDict):
    names: List[str]
    ids: List[str]


class DartResponse(TypedDict):
    status: str
    msg: str
