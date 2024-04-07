import pandas as pd
from config import ReportCodes
from config import ReportTypes
from config import FootnoteDataSjDivs
from config import Units
from corps import Corp
from reports import Report
from utils import get_api_key

API_KEY = get_api_key()


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

    @staticmethod
    def reset_index_df(df: pd.DataFrame) -> pd.DataFrame:
        return df.reset_index().drop(['index'], axis=1)

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
                target_df = self.refine_unit(target_df)
                annual_df = self.reset_index_df(pd.concat([annual_df, target_df]))

            for footnote_data_sj_div in FootnoteDataSjDivs:
                if footnote_data_sj_div == FootnoteDataSjDivs.EMPLOYEE_STATUS:
                    footnote_detail_df = report.get_employee_df()
                else:
                    footnote_detail_df = report.get_footnote_detail_df(footnote_data_sj_div=footnote_data_sj_div, unit=self.unit)

                annual_df = self.reset_index_df(pd.concat([annual_df, footnote_detail_df]))

            if annual_df.empty:
                return pd.DataFrame()

            return annual_df.rename(columns={"amount": str(year)})

        # 분기별 컬럼명 저장
        amount_cols = []

        # 각 항목별, 분기별 데이터프레임 저장
        dfs_by_sj_div = {}
        for i, report_code in enumerate(ReportCodes):
            amount_col_name = f"{str(year)}.{report_code.name}"
            report = Report(
                corp_code=self.corp_code,
                year=year,
                report_code=report_code,
                is_connected=self.is_connected,
                api_key=self.api_key,
            )

            has_quarter_data = False
            # 분기별 재무상태표, 손익계산서, 현금흐름표 정보 취합
            for report_type_idx, report_type in enumerate(ReportTypes):
                target_df = report.get_target_type_data(report_type=report_type)
                target_df = self.refine_unit(target_df)

                if report_type.name not in dfs_by_sj_div:
                    dfs_by_sj_div[report_type.name] = []
                dfs_by_sj_div[report_type.name].append({'col_name': amount_col_name, 'df': target_df})

                if report_type_idx == 0 and not target_df.empty:
                    has_quarter_data = True

            # 분기 데이터가 있을 때에만 컬럼명 저장
            if has_quarter_data:
                amount_cols.append(amount_col_name)

            for footnote_data_sj_div in FootnoteDataSjDivs:
                if footnote_data_sj_div.name not in dfs_by_sj_div:
                    dfs_by_sj_div[footnote_data_sj_div.name] = []

                if footnote_data_sj_div == FootnoteDataSjDivs.EMPLOYEE_STATUS:
                    df = report.get_employee_df()
                else:
                    df = report.get_footnote_detail_df(footnote_data_sj_div=footnote_data_sj_div, unit=self.unit)

                dfs_by_sj_div[footnote_data_sj_div.name].append({'col_name': amount_col_name, 'df': df})

        annual_df = pd.DataFrame()

        # 항목별, 분기별 데이터프레임을 연간 단위로 합치는 작업
        for sj_div in dfs_by_sj_div:
            sj_div_df = pd.DataFrame()

            for item in dfs_by_sj_div[sj_div]:
                df = item['df'].rename(columns={'amount': item['col_name']})
                if sj_div_df.empty:
                    sj_div_df = df
                else:
                    sj_div_df = pd.merge(left=sj_div_df, right=df, left_on=['sj_div', 'sj_nm', 'account_nm'], right_on=['sj_div', 'sj_nm', 'account_nm'], how='outer')
                    sj_div_df.fillna(0, inplace=True)

            for col in sj_div_df.columns:
                if sj_div_df[col].dtype in [int, float]:
                    sj_div_df[col] = sj_div_df[col].apply(int)

            annual_df = self.reset_index_df(pd.concat([annual_df, sj_div_df]))

        if annual_df.empty:
            return pd.DataFrame()

        # 누적 데이터인 경우 별도의 처리 없이 바로 return
        if is_accumulated:
            return annual_df

        sj_divs = annual_df.sj_div.unique().tolist()
        # 손익계산서, 현금흐름표, 비용의 성격별 분류 -> 누적값에 대한 계산 필요
        # 재무상태표, 재고자산 현황, 임직원 현황 -> 값 그대로 사용
        sj_divs_need_calculation = ['CIS', 'CF', FootnoteDataSjDivs.EXPENSE.name]

        # 계산의 편의를 위해 컬럼 역전. 기존에는 1분기 -> 4분기였다면, 4분기 -> 1분기 순으로 나열
        reversed_cols = list(reversed(amount_cols))

        merged = pd.DataFrame()

        for sj_div in sj_divs:
            sj_div_df = annual_df[annual_df.sj_div == sj_div].copy()

            if sj_div not in sj_divs_need_calculation:
                merged = self.reset_index_df(pd.concat([merged, sj_div_df]))
            else:
                for i, col in enumerate(reversed_cols):
                    try:
                        prev_quarter_col = reversed_cols[i + 1]
                        sj_div_df[col] = sj_div_df[col] - sj_div_df[prev_quarter_col]
                    except IndexError:
                        pass
                merged = self.reset_index_df(pd.concat([merged, sj_div_df]))

        return merged

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