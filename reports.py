import re

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from pydash import py_

from accounts import BalanceSheetAccounts
from accounts import CashFlowAccounts
from accounts import IncomeStatementAccounts
from accounts import get_account_detail
from config import BASE_URL
from config import AccountDetail
from config import DartResponse
from config import FootnoteDataSjDivs
from config import ReportCodes
from config import ReportTypes
from config import Units
from corps import Corp
from utils import get_api_key

API_KEY = get_api_key()


class Report:
    def __init__(
        self,
        corp_code: str,
        year: int,
        report_code: ReportCodes = ReportCodes.Q4,
        is_connected: bool = False,
        api_key: str = API_KEY,
    ):

        if not api_key:
            raise ValueError("API Key is not valid")

        self.corp_code = corp_code

        corp_inst = Corp(api_key=api_key)
        target_corp = corp_inst.find_by_code(corp_code)
        if not target_corp:
            raise ValueError("Invalid corp_code")

        self.corp_name = target_corp["corp_name"]
        self.year = str(year)
        self.report_code = report_code
        self.is_connected = is_connected
        self.api_key = api_key

        raw_df = self.get_raw_df()
        rcept_no = raw_df["rcept_no"].iloc[0]
        self.url = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=" + rcept_no
        self.raw_df = raw_df.drop(["rcept_no"], axis=1)

    @property
    def report_params(self):
        return {
            "crtfc_key": self.api_key,
            "corp_code": self.corp_code,
            "bsns_year": str(self.year),
            "reprt_code": self.report_code.value,
        }

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
            **self.report_params,
            "fs_div": "CFS" if self.is_connected else "OFS",
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

    def get_employee_df(self) -> pd.DataFrame:
        target_url = "https://opendart.fss.or.kr/api/empSttus.json"
        res = requests.get(target_url, params=self.report_params).json()

        if not self.check_data_valid(res):
            return pd.DataFrame()

        data = []
        for item in res["list"]:
            team = item["fo_bbm"]
            sex = item["sexdstn"]

            reg_employee_cnt = item["rgllbr_co"]
            irreg_employee_cnt = item["cnttk_co"]

            reg_employee_cnt = reg_employee_cnt.replace(",", "")
            irreg_employee_cnt = irreg_employee_cnt.replace(",", "")

            try:
                reg_employee_cnt = int(reg_employee_cnt)
            except ValueError:
                reg_employee_cnt = 0

            try:
                irreg_employee_cnt = int(irreg_employee_cnt)
            except ValueError:
                irreg_employee_cnt = 0

            for is_regular in [True, False]:
                data.append(
                    {
                        "sj_div": FootnoteDataSjDivs.EMPLOYEE_STATUS.name,
                        "sj_nm": "직원 등의 현황",
                        "account_nm": f'{team}_{sex}({"정규직" if is_regular else "계약직"})',
                        "amount": (
                            reg_employee_cnt if is_regular else irreg_employee_cnt
                        ),
                    }
                )

        return pd.DataFrame(data)

    def get_footnote_url(self):
        res = requests.get(self.url)

        reg = (
            "\s+node[12]\['text'\][ =]+\"(.*?)\"\;"
            "\s+node[12]\['id'\][ =]+\"(\d+)\";"
            "\s+node[12]\['rcpNo'\][ =]+\"(\d+)\";"
            "\s+node[12]\['dcmNo'\][ =]+\"(\d+)\";"
            "\s+node[12]\['eleId'\][ =]+\"(\d+)\";"
            "\s+node[12]\['offset'\][ =]+\"(\d+)\";"
            "\s+node[12]\['length'\][ =]+\"(\d+)\";"
            "\s+node[12]\['dtd'\][ =]+\"(.*?)\";"
            "\s+node[12]\['tocNo'\][ =]+\"(\d+)\";"
        )

        matches = re.findall(reg, res.text)

        if not matches:
            return None

        candidates = py_.filter(matches, lambda m: "주석" in m[0])

        if self.is_connected:
            target = py_.find(candidates, lambda m: "연결" in m[0])

        target = py_.find(candidates, lambda m: "연결" not in m[0])

        if not target:
            return None

        viewer_url = "http://dart.fss.or.kr/report/viewer.do?"
        return f"{viewer_url}rcpNo={target[2]}&dcmNo={target[3]}&eleId={target[4]}&offset={target[5]}&length={target[6]}&dtd={target[7]}"

    def get_footnote_detail_df(
        self, footnote_data_sj_div: FootnoteDataSjDivs, unit: Units = Units.DEFAULT
    ) -> pd.DataFrame:
        footnote_url = self.get_footnote_url()

        if not footnote_url:
            return pd.DataFrame()
        res = requests.get(footnote_url)
        soup = bs(res.text, "html.parser")

        target_header = None
        if footnote_data_sj_div == FootnoteDataSjDivs.EXPENSE:
            pair = re.compile(r"\d+\. 비용")
            sj_div = FootnoteDataSjDivs.EXPENSE.name
            sj_nm = "비용의 성격별 분류"
        elif footnote_data_sj_div == FootnoteDataSjDivs.INVENTORY:
            pair = re.compile(r"\d+\. 재고자산")
            sj_div = FootnoteDataSjDivs.INVENTORY.name
            sj_nm = "재고자산 내역"
        else:
            raise ValueError("Not proper detail_data_type")

        for tag in soup.find_all("p"):
            if pair.match(tag.text):
                target_header = tag
                break
        if not target_header:
            return pd.DataFrame()

        unit_table = None
        for tag in target_header.find_next_siblings():
            if tag.name == "table":
                unit_table = tag
                break

        if not unit_table:
            return pd.DataFrame()

        unit_match = re.search(r"단위 : (.+)\)", unit_table.text.strip())

        if not unit_match:
            return pd.DataFrame()

        table_unit = unit_match.group(1).replace(" ", "")
        if table_unit == "원":
            unit_num = 1
        elif table_unit == "천원":
            unit_num = 1000
        elif table_unit == "백만원":
            unit_num = 1000 * 1000
        else:
            raise ValueError(
                f"Invalid unit in footnote data in {self.corp_name} {self.report_code} {footnote_data_sj_div.name}"
            )

        # 단위 조정
        multiplied_by = unit_num / unit.value

        content_table = None
        for tag in unit_table.find_next_siblings():
            if tag.name == "table":
                content_table = tag
                break

        if not content_table:
            return pd.DataFrame()

        theads = content_table.find("thead").find_all("th")

        # Nested column
        if py_.some(theads, lambda th: th.get("colspan")):
            col_index = int(
                py_.find(theads, lambda th: th.get("colspan")).get("colspan")
            )
        else:
            col_index = len(theads) - 1

        # Extract data rows
        data = []
        for row in content_table.find("tbody").find_all("tr"):
            account_nm = (
                row.find_all("td")[0].text.strip().replace("\xa0", "").replace(" ", "")
            )
            account_nm = re.sub(r"\[\s]", "", account_nm)
            amount = row.find_all("td")[col_index].text.strip().replace(",", "")

            try:
                amount_num = eval(amount)
                # negative value
                if re.match(r"\(\d+\)", amount):
                    amount = -1 * amount_num
                else:
                    amount = amount_num

            except SyntaxError:
                amount = 0

            data.append(
                {
                    "sj_div": sj_div,
                    "sj_nm": sj_nm,
                    "account_nm": account_nm,
                    "amount": int(amount * multiplied_by),
                }
            )

        return pd.DataFrame(data)

    def get_raw_df(self) -> pd.DataFrame:
        data = self.get_data()
        if not self.check_data_valid(data):
            return pd.DataFrame()

        df = pd.DataFrame(data["list"])
        target_columns = [
            "rcept_no",
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

        # 표준계정코드 미사용의 경우 계정과목명으로 비교
        # 이 과정에서 중복되는 행 발생할 수 있음 (띄어쓰기 비교)
        filtered.drop_duplicates(inplace=True)

        # 분기 데이터
        values = filtered.thstrm_amount.values
        # 분기 누적 데이터
        acc_values = filtered.thstrm_add_amount.values

        total = 0
        for val, acc_val in zip(values, acc_values):
            # 값이 없는 경우를 제외하면 기본적으로 누적값 사용
            # 분기별로 값을 처리하는 과정은 get_annual_data 함수에서 따로 진행
            target_val = val if pd.isnull(acc_val) or not acc_val else acc_val
            try:
                parsed = int(target_val)
                total += parsed
            except ValueError:
                continue

        return total

    def get_target_type_data(self, report_type: ReportTypes) -> pd.DataFrame:
        if self.raw_df.empty:
            return pd.DataFrame()

        target_df = self.raw_df[self.raw_df.sj_div == report_type.name]
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
                    "sj_div": report_type.name,
                    "sj_nm": report_type.value,
                    "account_nm": account.value,
                    "amount": self.get_account_amount(
                        target_df, account_detail=account_detail
                    ),
                }
            )
        return pd.DataFrame(rows)
