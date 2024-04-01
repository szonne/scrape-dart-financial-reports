from typing import TypedDict

import pandas as pd
import requests

from config import BASE_URL
from config import ReportCodes


class AccountDetail(TypedDict):
    names: list[str]
    ids: list[str]


class DartResponse(TypedDict):
    status: str
    msg: str


class Report:
    @staticmethod
    def get_data(
        api_key: str,
        corp_code: str,
        year: int,
        report_code: ReportCodes = ReportCodes.Q4,
        is_connected=False,
    ) -> DartResponse:
        params = {
            "crtfc_key": api_key,
            "corp_code": corp_code,
            "fs_div": "CFS" if is_connected else "OFS",
            "bsns_year": str(year),
            "reprt_code": report_code.value,
        }

        res = requests.get(BASE_URL + "/fnlttSinglAcntAll.json", params=params)
        return res.json()

    @staticmethod
    def check_res_valid(res: DartResponse):
        if res["status"] == "013":
            return False

        if "list" not in res:
            return False

        return True

    @staticmethod
    def filter_accounts(
        report_df: pd.DataFrame, account_detail: AccountDetail
    ) -> pd.DataFrame:
        filtered = pd.DataFrame()

        names = account_detail["names"]
        ids = account_detail["ids"]

        for id in ids:
            target_df = report_df[report_df.account_id == id]
            filtered = pd.concat([filtered, target_df])

        # 표준계정코드 미사용하는 경우 계정과목명과 직접 대조
        for name in names:
            stripped_name = name.replace(" ", "")
            target_df = report_df[
                (report_df.account_id == "-표준계정코드 미사용-")
                & (
                    report_df.account_nm.apply(
                        lambda val: val.replace(" ", "") == stripped_name
                    )
                )
            ]
            filtered = pd.concat([filtered, target_df])

        return filtered
