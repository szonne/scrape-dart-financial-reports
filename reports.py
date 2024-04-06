import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

from accounts import BalanceSheetAccounts
from accounts import CashFlowAccounts
from accounts import IncomeStatementAccounts
from accounts import get_account_detail
from config import BASE_URL
from config import AccountDetail
from config import DartResponse
from config import ReportCodes
from config import ReportTypes
from config import Units
from corps import Corp
from utils import get_api_key
from pydash import py_
import re

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

        candidates = py_.filter(matches, lambda m: '주석' in m[0])

        if self.is_connected:
            target = py_.find(candidates, lambda m: '연결' in m[0])

        target = py_.find(candidates, lambda m: '연결' not in m[0])

        if not target:
            return None

        viewer_url = 'http://dart.fss.or.kr/report/viewer.do?'
        return f'{viewer_url}rcpNo={target[2]}&dcmNo={target[3]}&eleId={target[4]}&offset={target[5]}&length={target[6]}&dtd={target[7]}'

    def get_inventory_detail_df(self, unit: Units = Units.DEFAULT) -> pd.DataFrame:
        res = requests.get(self.get_footnote_url())
        soup = bs(res.text, 'html.parser')

        target_header = None
        pair = re.compile(r'\d+\. 재고자산')
        for tag in soup.find_all('p'):
            if pair.match(tag.text):
                target_header = tag
                break

        if not target_header:
            return pd.DataFrame()

        unit_table = target_header.find_next_sibling()
        unit_match = re.search(r'단위 : (.+)\)', unit_table.text.strip())

        if not unit_match:
            return pd.DataFrame()

        inventory_unit = unit_match.group(1).replace(' ', '')

        if inventory_unit == '원':
            unit_num = 1
        elif inventory_unit == '천원':
            unit_num = 1000
        elif inventory_unit == '백만원':
            unit_num = 1000 * 1000
        else:
            raise ValueError(f'Invalid unit in inventory detail in {self.corp_name} {self.report_code}')

        # 단위 조정
        multiplied_by = unit_num / unit.value

        content_table = unit_table.find_next_sibling()

        theads = content_table.find('thead').find_all('th')
        col_index = 0
        for th_idx, th in enumerate(theads):
            if th.get('colspan'):
                col_index += int(th.get('colspan'))
            else:
                if th_idx != 0:
                    col_index += 1

            if py_.some(['당기', '당반기', '당분기'], lambda keyword: keyword in th.text.strip()):
                break

        # Extract data rows
        data = []
        for row in content_table.find('tbody').find_all('tr'):
            account_nm = row.find_all('td')[0].text.strip().replace('\xa0', '').replace(' ', '')
            account_nm = re.sub(r'\[\s]', "", account_nm)
            amount = row.find_all('td')[col_index].text.strip().replace(',', '')


            try:
                # negative value
                if re.match(r'\(\d+\)', amount):
                    amount = eval(amount) * -1
                else:
                    amount = eval(amount)
            except SyntaxError:
                amount = 0

            data.append({'account_nm': account_nm, 'amount': int(amount * multiplied_by)})

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


class ReportCalculator:
    def __init__(
        self,
        corp_name: str = None,
        corp_code: str = None,
        is_connected: bool = False,
        unit: Units = Units.DEFAULT,
        api_key: str = API_KEY,
    ):
        if not corp_code and not corp_name:
            raise ValueError("Either corp_name or corp_code should be vaild")

        corp_inst = Corp(api_key=api_key)
        if corp_code:
            target_corp = corp_inst.find_by_code(code=corp_code)
        if corp_name:
            target_corp = corp_inst.find_by_name(name=corp_name)

        if not target_corp:
            raise ValueError("Invalid corp_code")

        self.corp_code = target_corp["corp_code"]
        self.corp_name = target_corp["corp_name"]
        self.is_connected = is_connected
        self.unit = unit
        self.api_key = None
        if api_key:
            self.api_key = api_key

    def refine_unit(self, df):
        for col in df.columns:
            if df[col].dtype == int:
                df[col] = df[col].apply(lambda val: int(val / self.unit.value))

        return df

    def get_annual_data(
        self, year: int, by_quarter: bool = True, is_accumulated: bool = False
    ):
        """
        :param year
        :param is_accumulated: True -> 별도의 처리없이 누적값 리턴
        :param by_quarter: False -> 연간사업보고서 값만 리턴, True -> 분기별 보고서 리턴
        :return:
        """
        # 연간사업보고서 정보만 취합
        if not by_quarter:
            report = Report(
                corp_code=self.corp_code,
                year=year,
                report_code=ReportCodes.Q4,
                is_connected=self.is_connected,
                api_key=self.api_key,
            )

            annual_df = pd.DataFrame()
            for report_type in ReportTypes:
                target_df = report.get_target_type_data(report_type=report_type)
                annual_df = pd.concat([annual_df, target_df])

            if annual_df.empty:
                return pd.DataFrame()

            annual_df.rename(columns={"amount": str(year)}, inplace=True)
            return self.refine_unit(annual_df)

        # 분기별 정보 취합
        annual_df = pd.DataFrame()

        # 분기별 컬럼명 저장
        amount_cols = []

        for i, report_code in enumerate(ReportCodes):
            amount_col_name = f"{str(year)}.{report_code.name}"
            report = Report(
                corp_code=self.corp_code,
                year=year,
                report_code=report_code,
                is_connected=self.is_connected,
                api_key=self.api_key,
            )

            quarter_df = pd.DataFrame()

            # 분기별 재무상태표, 손익계산서, 현금흐름표 정보 취합
            for report_type in ReportTypes:
                target_df = report.get_target_type_data(report_type=report_type)
                quarter_df = pd.concat([quarter_df, target_df])

            if quarter_df.empty:
                continue

            # 분기 데이터가 있을 때에만 컬럼명 저장
            amount_cols.append(amount_col_name)
            quarter_df.rename(columns={"amount": amount_col_name}, inplace=True)

            # 1분기 데이터이거나 혹은 이전 분기까지 데이터가 없었던 경우(ex. Q2부터 사업보고서 나오기 시작한 case)
            if i == 0 or annual_df.empty:
                annual_df = quarter_df.copy()

            # 분기 데이터를 새 열에 추가
            else:
                annual_df[amount_col_name] = quarter_df[amount_col_name]

        # 누적 데이터인 경우 별도의 처리 없이 바로 return
        if is_accumulated:
            return self.refine_unit(annual_df)

        if annual_df.empty:
            return pd.DataFrame()

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
        merged = pd.concat([bs_df, leftover_df])
        return self.refine_unit(merged)

    def get_annual_data_by_period(
        self, start_year: int, end_year: int, by_quarter=True, is_accumulated=False
    ):
        total_df = pd.DataFrame()
        join_on_columns = ["sj_div", "sj_nm", "account_nm"]

        for i, year in enumerate(range(start_year, end_year + 1)):
            annual_data = self.get_annual_data(
                year=year, by_quarter=by_quarter, is_accumulated=is_accumulated
            )
            if i == 0:
                total_df = annual_data.copy()
            else:
                total_df = pd.merge(
                    total_df,
                    annual_data,
                    left_on=join_on_columns,
                    right_on=join_on_columns,
                )

        # Drop unused column
        total_df.drop(["sj_div"], axis=1, inplace=True)

        return total_df

    def write_data(
        self,
        start_year: int,
        end_year: int,
        is_accumulated: bool = False,
        filename=None,
        cell_width=None,
    ):
        df_by_quarter = self.get_annual_data_by_period(
            start_year=start_year,
            end_year=end_year,
            is_accumulated=is_accumulated,
            by_quarter=True,
        )

        df_by_year = self.get_annual_data_by_period(
            start_year=start_year,
            end_year=end_year,
            is_accumulated=is_accumulated,
            by_quarter=False,
        )

        if not filename:
            filename = f"{self.corp_name}_{str(start_year)}_{str(end_year)}_unit_{self.unit.name.lower()}.xlsx"

        # Formatting cell width in excel file
        if not cell_width:
            if self.unit == Units.DEFAULT:
                cell_width = 15
            elif self.unit == Units.THOUSAND:
                cell_width = 12
            else:
                cell_width = 9

        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            df_by_quarter.to_excel(
                writer,
                sheet_name="Quarter",
                index=False,
                header=True,
                float_format="#,###",
            )
            df_by_year.to_excel(
                writer,
                sheet_name="Year",
                index=False,
                header=True,
                float_format="#,###",
            )

            workbook = writer.book
            float_format = workbook.add_format({"num_format": "#,##0"})
            for worksheet in [writer.sheets["Quarter"], writer.sheets["Year"]]:
                worksheet.set_column(
                    0, 1000, width=cell_width, cell_format=float_format
                )
