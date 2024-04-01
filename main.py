from corps import Corp
from reports import ReportCalculator

if __name__ == "__main__":
    corp_list = Corp.get_list()
    target_corp = Corp.find_by_name(corp_list, "원텍")

    report_calculator = ReportCalculator(
        corp_code=target_corp["corp_code"], is_connected=True
    )
    df = report_calculator.get_annual_data_by_period(
        start_year=2021, end_year=2023, by_quarter=True, is_accumulated=False
    )

    df.to_excel("원텍.xlsx", index=False)
