import pandas as pd
import requests

from accounts import BalanceSheetAccounts
from accounts import CashFlowAccounts
from accounts import IncomeStatementAccounts
from accounts import get_account_detail
from auth import API_KEY
from config import BASE_URL
from config import AccountDetail
from config import DartResponse
from config import ReportCodes
from config import ReportTypes
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
        self.raw_df = self.get_raw_df()

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

    def get_raw_df(self) -> pd.DataFrame:
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
            "thstrm_add_amount",
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
        acc_values = filtered.thstrm_add_amount.values

        total = 0
        for val, acc_val in zip(values, acc_values):
            target_val = val if pd.isnull(acc_val) or not acc_val else acc_val
            try:
                parsed = int(target_val)
                total += parsed
            except ValueError:
                continue

        return total

    def get_target_type_data(self, report_type: ReportTypes) -> pd.DataFrame:
        report_name = report_type.name
        target_df = self.raw_df[self.raw_df.sj_div == report_name]
        if report_type == ReportTypes.BS:
            target_accounts = BalanceSheetAccounts
        elif report_type == ReportTypes.CIS:
            target_accounts = IncomeStatementAccounts
        else:
            target_accounts = CashFlowAccounts

        rows = []
        for account in target_accounts:
            account_detail = get_account_detail(report_type, account)
            rows.append(
                {
                    "sj_div": report_name,
                    "sj_nm": "재무상태표",
                    "account_nm": account.value,
                    "amount": self.get_account_amount(
                        target_df, account_detail=account_detail
                    ),
                }
            )
        return pd.DataFrame(rows)


class ReportCalculator:
    def __init__(self, corp_code: str, is_connected: bool = False):
        self.corp_code = corp_code
        self.is_connected = is_connected

    def get_annual_data(
        self, year: int, by_quarter: bool = True, is_accumulated: bool = False
    ):
        """
        :param year
        :param is_accumulated: True -> 별도의 처리없이 누적값 리턴
        :param by_quarter: False -> 연간사업보고서 값만 리턴, True -> 분기별 보고서 리턴
        :return:
        """
        annual_df = pd.DataFrame()
        amount_cols = []
        for i, report_code in enumerate(ReportCodes):

            if not by_quarter and report_code != ReportCodes.Q4:
                continue

            if by_quarter:
                amount_col_name = f"{str(year)}.{report_code.name}"
            else:
                amount_col_name = str(year)

            amount_cols.append(amount_col_name)
            report = Report(
                corp_code=self.corp_code,
                year=year,
                report_code=report_code,
                is_connected=self.is_connected,
            )

            quarter_df = pd.DataFrame()
            for report_type in ReportTypes:
                target_df = report.get_target_type_data(report_type=report_type)
                quarter_df = pd.concat([quarter_df, target_df])

            quarter_df.rename(columns={"amount": amount_col_name}, inplace=True)

            if not by_quarter or i == 0:
                annual_df = quarter_df.copy()
            else:
                annual_df[amount_col_name] = quarter_df[amount_col_name]

        if not by_quarter:
            return annual_df

        if is_accumulated:
            return annual_df

        # 손익계산서, 현금흐름표는 누적값이므로 별도 처리
        bs_df = annual_df[annual_df.sj_div == "BS"].copy()
        leftover_df = annual_df[annual_df.sj_div != "BS"].copy()

        reversed_cols = list(reversed(amount_cols))
        for i, col in enumerate(reversed_cols):
            try:
                prev_quarter_col = reversed_cols[i + 1]
                leftover_df[col] = leftover_df[col] - leftover_df[prev_quarter_col]
            except IndexError:
                pass
        return pd.concat([bs_df, leftover_df])

    # Todo. 중간에 데이터가 없는 경우 처리
    # 원텍 2022년 2분기부터 데이터 있음
    def get_annual_data_by_period(
        self, start_year: int, end_year: int, by_quarter=True, is_accumulated=False
    ):
        total_df = pd.DataFrame()
        amount_col_num = 4 if by_quarter else 1
        join_on_columns = None

        for i, year in enumerate(range(start_year, end_year + 1)):
            annual_data = self.get_annual_data(
                year=year, by_quarter=by_quarter, is_accumulated=is_accumulated
            )
            if i == 0:
                total_df = annual_data.copy()
                join_on_columns = list(total_df.columns)[:-amount_col_num]
            else:
                total_df = pd.merge(
                    total_df,
                    annual_data,
                    left_on=join_on_columns,
                    right_on=join_on_columns,
                )

        return total_df
