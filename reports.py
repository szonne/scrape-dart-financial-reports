import pandas as pd
import requests

from accounts import BalanceSheetAccounts
from accounts import CashFlowAccounts
from accounts import IncomeStatementAccounts
from accounts import get_bs_account_detail
from accounts import get_cf_account_detail
from accounts import get_cis_account_detail
from auth import API_KEY
from config import BASE_URL
from config import AccountDetail
from config import DartResponse
from config import ReportCodes
from corps import Corp


class Report:
    def __init__(
        self,
        corp_code: str,
        year: int,
        report_code: ReportCodes = ReportCodes.Q4,
        is_connected=False,
    ):
        self.corp_code = corp_code
        self.year = str(year)
        self.report_code = report_code
        self.is_connected = is_connected
        self.api_key = API_KEY
        self.df = self.get_df()

    @property
    def corp_name(self) -> str:
        corp_inst = Corp()
        corp_list = corp_inst.get_list()
        target_corp = corp_inst.find_by_code(corp_list=corp_list, code=self.corp_code)

        if target_corp:
            return target_corp["corp_name"]
        return ""

    def get_data(self) -> DartResponse:
        """
        :param corp_code:
        :param year:
        :param report_code:
        :param is_connected: True일 경우 '연결', False일 경우 '별도'
        :param api_key:
        :return:
        """
        params = {
            "crtfc_key": self.api_key,
            "corp_code": self.corp_code,
            "fs_div": "CFS" if self.is_connected else "OFS",
            "bsns_year": str(self.year),
            "reprt_code": self.report_code.value,
        }

        res = requests.get(BASE_URL + "/fnlttSinglAcntAll.json", params=params)
        return res.json()

    @staticmethod
    def check_data_valid(res: DartResponse):
        if res["status"] == "013":
            return False

        if "list" not in res:
            return False

        return True

    def get_df(self) -> pd.DataFrame:
        data = self.get_data()
        if not self.check_data_valid(data):
            return pd.DataFrame()

        df = pd.DataFrame(data["list"])
        target_columns = [
            "bsns_year",
            "corp_code",
            "sj_div",
            "sj_nm",
            "account_id",
            "account_nm",
            "account_detail",
            "thstrm_nm",
            "thstrm_amount",
        ]

        return df[target_columns]

    @staticmethod
    def get_account_amount(
        report_df: pd.DataFrame, account_detail: AccountDetail
    ) -> int:
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

        values = filtered.thstrm_amount.values
        total = 0
        for val in values:
            try:
                parsed = int(val)
                total += parsed
            except ValueError:
                continue

        return total

    def get_bs_data(self) -> pd.DataFrame:
        # 재무상태표 (Balance sheet)
        bs_df = self.df[self.df.sj_div == "BS"]
        thstrm_nm = bs_df.thstrm_nm.iloc[0]
        rows = []
        for account in BalanceSheetAccounts:
            account_detail = get_bs_account_detail(account)
            rows.append(
                {
                    "year": self.year,
                    "sj_div": "BS",
                    "sj_nm": "재무상태표",
                    "thstrm_nm": thstrm_nm,
                    "account_nm": account.value,
                    "amount": self.get_account_amount(
                        bs_df, account_detail=account_detail
                    ),
                }
            )

        return pd.DataFrame(rows)

    def get_cis_data(self) -> pd.DataFrame:
        # 포괄손익계산서 (Comprehensive Income Statement)
        cis_df = self.df[self.df.sj_div == "CIS"]
        thstrm_nm = cis_df.thstrm_nm.iloc[0]
        rows = []
        for account in IncomeStatementAccounts:
            account_detail = get_cis_account_detail(account)
            rows.append(
                {
                    "year": self.year,
                    "sj_div": "CIS",
                    "sj_nm": "포괄손익계산서",
                    "thstrm_nm": thstrm_nm,
                    "account_nm": account.value,
                    "amount": self.get_account_amount(
                        cis_df, account_detail=account_detail
                    ),
                }
            )

        return pd.DataFrame(rows)

    def get_cf_data(self) -> pd.DataFrame:
        # 현금흐름표 (Cash flow)
        cf_df = self.df[self.df.sj_div == "CF"]
        thstrm_nm = cf_df.thstrm_nm.iloc[0]
        rows = []
        for account in CashFlowAccounts:
            account_detail = get_cf_account_detail(account)
            rows.append(
                {
                    "year": self.year,
                    "sj_div": "CF",
                    "sj_nm": "현금흐름표",
                    "thstrm_nm": thstrm_nm,
                    "account_nm": account.value,
                    "amount": self.get_account_amount(
                        cf_df, account_detail=account_detail
                    ),
                }
            )

        return pd.DataFrame(rows)


class ReportCalculator:
    def __init__(self, corp_code: str, year: int, is_connected: bool = False):
        self.corp_code = corp_code
        self.year = year
        self.is_connected = is_connected

    def get_annual_bs_data(self, is_accumulated: bool = False):
        """
        :param is_accumulated: True면 1->4분기 보고서까지 별도의 처리없이 누적값 리턴
        :return:
        """
        df = pd.DataFrame()
        for report_code in ReportCodes:
            amount_col_name = f"{str(self.year)}.{report_code.name}"
            report = Report(
                corp_code=self.corp_code,
                year=self.year,
                report_code=report_code.value,
                is_connected=self.is_connected,
            )
