import pandas as pd

from config import Units
from corps import Corp
from reports import ReportCalculator

if __name__ == "__main__":
    corp_list = Corp.get_list()
    target_corp = Corp.find_by_name(corp_list, "원텍")

    report_calculator = ReportCalculator(
        corp_code=target_corp["corp_code"], is_connected=True, unit=Units.MILLION
    )

    start_year = 2022
    end_year = 2023

    quarter_df = report_calculator.get_annual_data_by_period(
        start_year=start_year, end_year=end_year, by_quarter=True, is_accumulated=False
    )
    annual_df = report_calculator.get_annual_data_by_period(
        start_year=start_year, end_year=end_year, by_quarter=False
    )

    if report_calculator.unit == Units.DEFAULT:
        cell_width = 15
    elif report_calculator.unit == Units.THOUSAND:
        cell_width = 12
    else:
        cell_width = 9

    filename = f"{target_corp['corp_name']}_{str(start_year)}_{str(end_year)}_unit_{report_calculator.unit.name.lower()}.xlsx"
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        quarter_df.to_excel(
            writer, sheet_name="Quarter", index=False, header=True, float_format="#,###"
        )
        annual_df.to_excel(
            writer, sheet_name="Year", index=False, header=True, float_format="#,###"
        )

        workbook = writer.book
        float_format = workbook.add_format({"num_format": "#,##0"})
        for worksheet in [writer.sheets["Quarter"], writer.sheets["Year"]]:
            worksheet.set_column(0, 1000, width=cell_width, cell_format=float_format)
