import pandas as pd
from corps import Corp
from reports import ReportCalculator
from config import Units

if __name__ == "__main__":
    corp_list = Corp.get_list()
    target_corp = Corp.find_by_name(corp_list, "원텍")

    report_calculator = ReportCalculator(
        corp_code=target_corp["corp_code"], is_connected=True, unit=Units.THOUSAND
    )

    start_year = 2022
    end_year = 2023

    quarter_df = report_calculator.get_annual_data_by_period(
        start_year=start_year, end_year=end_year, by_quarter=True, is_accumulated=False
    )
    annual_df = report_calculator.get_annual_data_by_period(
        start_year=start_year, end_year=end_year, by_quarter=False
    )

    with pd.ExcelWriter('원텍_단위_천원.xlsx', engine='openpyxl') as writer:
        quarter_df.to_excel(writer, sheet_name='Quarter', index=False, header=True)
        annual_df.to_excel(writer, sheet_name='Year', index=False, header=True)


