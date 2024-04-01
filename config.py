from enum import Enum
from typing import List
from typing import TypedDict

BASE_URL = "https://opendart.fss.or.kr/api"


class ReportCodes(Enum):
    Q1 = "11013"
    Q2 = "11012"
    Q3 = "11014"
    Q4 = "11011"


class ReportTypes(Enum):
    BS = "재무상태표"
    CIS = "포괄손익계산서"
    CF = "현금흐름표"


# Currency = Korean WON
class Units(Enum):
    DEFAULT = 1
    THOUSAND = 1000
    MILLION = 1000 * 1000

class AccountDetail(TypedDict):
    names: List[str]
    ids: List[str]


class DartResponse(TypedDict):
    status: str
    msg: str
