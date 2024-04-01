from enum import Enum

from config import ReportTypes


class BalanceSheetAccounts(Enum):
    CURRENT_ASSETS = "유동자산"
    CASH_AND_CASH_EQUIVALENTS = "현금및현금성자산"
    TRADE_AND_OTHER_CURRENT_RECEIVABLES = "매출채권 및 기타채권"
    OTHER_CURRENT_ASSETS = "기타유동자산"
    INVENTORIES = "재고자산"

    NON_CURRENT_ASSETS = "비유동자산"
    TRADE_AND_OTHER_NON_CURRENT_RECEIVABLES = "매출채권 및 기타채권(비유동)"
    OTHER_NON_CURRENT_ASSETS = "기타비유동자산"
    PROPERTY_PLANT_AND_EQUIPMENT = "유형자산"
    INTANGIBLE_ASSETS = "무형자산"

    ASSETS = "자산총계"

    CURRENT_LIABILITIES = "유동부채"
    TRADE_AND_OTHER_CURRENT_PAYABLES = "매입채무 및 기타채무"
    SHORT_TERM_BORROWINGS = "단기차입금"
    CURRENT_CONVERTIBLE_BONDS = "전환사채(유동)"
    SHORT_TERM_INCOME_RECEIVED_IN_ADVANCE = "선수수익(유동)"
    SHORT_TERM_ADVANCES_CUSTOMERS = "선수금(유동)"
    # Todo. 비유동 선수수익, 선수금

    NON_CURRENT_LIABILITIES = "비유동부채"
    TRADE_AND_OTHER_NON_CURRENT_PAYABLES = "매입채무 및 기타채무(비유동)"
    LONG_TERM_BORROWINGS = "장기차입금"
    NON_CURRENT_CONVERTIBLE_BONDS = "전환사채(비유동)"
    LONG_TERM_INCOME_RECEIVED_IN_ADVANCE = "선수수익(비유동)"
    LONG_TERM_ADVANCES_CUSTOMERS = "선수금(비유동)"

    LIABILITIES = "부채총계"

    ISSUED_CAPITAL = "자본금"
    RETAINED_EARNINGS = "이익잉여금"
    EQUITY = "자본총계"

    EQUITY_AND_LIABILITIES = "자본과부채총계"


class IncomeStatementAccounts(Enum):
    REVENUE = "매출액"
    REVENUE_FROM_SALE_OF_GOODS_PRODUCT = "제품매출액"
    REVENUE_FROM_SALE_OF_GOODS_MERCHANDISE = "상품매출액"

    COST_OF_SALES = "매출원가"
    COST_OF_SALES_FROM_SALE_OF_GOODS_PRODUCT = "제품매출원가"
    COST_OF_SALES_FROM_SALE_OF_GOODS_MERCHANDISE = "상품매출원가"

    GROSS_PROFIT = "매출총이익"

    SELLING_GENERAL_ADMINISTRATIVE_EXPENSES = "판매비와관리비"
    OPERATING_INCOME_LOSS = "영업이익"

    PROFIT_LOSS = "당기순이익"


class CashFlowAccounts(Enum):
    OPERATING_ACTIVITIES = "영업활동현금흐름"
    PROFIT_LOSS = "당기순이익"
    # Todo. 분류가 명확하지 않은 경우가 너무 많음
    # ADJUSTMENTS_FOR_ASSETS_LIABILITIES_OF_OPERATING_ACTIVITIES = (
    #     "영업으로부터 창출된 현금흐름"
    # )
    INTEREST_PAID = "이자지급"
    INTEREST_RECEIVED = "이자수취"

    INVESTING_ACTIVITIES = "투자활동현금흐름"
    PURCHASE_OF_FINANCIAL_INSTRUMENTS = "금융상품의 취득"
    SALES_OF_FINANCIAL_INSTRUMENTS = "금융상품의 처분"
    PURCHASE_OF_PROPERTY_PLANT_AND_EQUIPMENT = "유형자산의 취득"
    SALES_OF_PROPERTY_PLANT_AND_EQUIPMENT = "유형자산의 처분"

    FINANCING_ACTIVITIES = "재무활동현금흐름"
    PROCEEDS_FROM_BORROWINGS = "차입금의 증가"
    REPAYMENTS_OF_BORROWINGS = "차입금의 감소"
    DIVIDENDS_PAID = "배당금 지급"


def get_account_detail(report_type, account):
    if report_type == ReportTypes.BS:
        return get_bs_account_detail(account)
    if report_type == ReportTypes.CIS:
        return get_cis_account_detail(account)
    if report_type == ReportTypes.CF:
        return get_cf_account_detail(account)


def get_bs_account_detail(account: BalanceSheetAccounts):
    if account == BalanceSheetAccounts.ASSETS:
        return {"names": ["자산총계"], "ids": ["ifrs-full_Assets"]}

    if account == BalanceSheetAccounts.CURRENT_ASSETS:
        return {"names": ["유동자산"], "ids": ["ifrs-full_CurrentAssets"]}
    if account == BalanceSheetAccounts.CASH_AND_CASH_EQUIVALENTS:
        return {
            "names": ["현금및현금성자산"],
            "ids": [
                "ifrs-full_CashAndCashEquivalents",
                "ifrs-full_Cash",
                "ifrs-full_CashEquivalents",
            ],
        }
    if account == BalanceSheetAccounts.TRADE_AND_OTHER_CURRENT_RECEIVABLES:
        return {
            "names": [
                "매출채권",
                "매출채권및기타채권",
                "매출채권 및 기타수취채권",
                "매출채권 및 기타채권",
            ],
            "ids": [
                "ifrs-full_TradeAndOtherCurrentReceivables",
                "dart_ShortTermTradeReceivable",
                "dart_AllowanceForDoubtfulAcccountShortTermTradeReceivable",
                "ifrs-full_TradeReceivables",
            ],
        }
    if account == BalanceSheetAccounts.OTHER_CURRENT_ASSETS:
        return {
            "names": ["기타유동자산"],
            "ids": ["ifrs-full_OtherCurrentAssets", "dart_OtherCurrentAssets"],
        }
    if account == BalanceSheetAccounts.INVENTORIES:
        return {
            "names": ["재고자산"],
            "ids": [
                "ifrs-full_Inventories",
                "dart_RawMaterialsGross",
                "ifrs-full_InventoriesTotal",
            ],
        }

    if account == BalanceSheetAccounts.NON_CURRENT_ASSETS:
        return {"names": ["비유동자산"], "ids": ["ifrs-full_NoncurrentAssets"]}
    if account == BalanceSheetAccounts.TRADE_AND_OTHER_NON_CURRENT_RECEIVABLES:
        return {
            "names": [
                "매출채권(비유동)",
                "장기매출채권",
                "장기매출채권및기타채권",
                "장기매출채권 및 기타채권",
                "비유동매출채권 및 기타채권",
                "장기성매출채권",
                "매출채권및상각후원가측정금융자산(비유동)",
            ],
            "ids": [
                "dart_LongTermTradeReceivablesGross",
                "dart_LongTermTradeAndOtherNonCurrentReceivablesGross",
                "dart_AllowanceForDoubtfulAcccountLongTermTradeReceivablesGross",
                "ifrs-full_NoncurrentTradeReceivables",
                "ifrs-full_NoncurrentReceivables",
            ],
        }
    if account == BalanceSheetAccounts.OTHER_NON_CURRENT_ASSETS:
        return {
            "names": ["기타비유동자산"],
            "ids": ["ifrs-full_OtherNoncurrentAssets", "dart_OtherNonCurrentAssets"],
        }
    if account == BalanceSheetAccounts.PROPERTY_PLANT_AND_EQUIPMENT:
        return {
            "names": ["유형자산"],
            "ids": [
                "ifrs-full_PropertyPlantAndEquipment",
                "dart_OtherPropertyPlantAndEquipmentGross",
            ],
        }
    if account == BalanceSheetAccounts.INTANGIBLE_ASSETS:
        return {
            "names": ["무형자산", "무형자산 및 영업권", "기타무형자산"],
            "ids": [
                "ifrs-full_IntangibleAssetsOtherThanGoodwill",
                "dart_OtherIntangibleAssetsGross",
                "dart_GoodwillGross",
                "ifrs-full_IntangibleAssetsAndGoodwill",
                "ifrs-full_OtherNoncurrentFinancialAssets",
            ],
        }

    if account == BalanceSheetAccounts.LIABILITIES:
        return {"names": ["부채총계"], "ids": ["ifrs-full_Liabilities"]}

    if account == BalanceSheetAccounts.CURRENT_LIABILITIES:
        return {"names": ["유동부채"], "ids": ["ifrs-full_CurrentLiabilities"]}
    if account == BalanceSheetAccounts.TRADE_AND_OTHER_CURRENT_PAYABLES:
        return {
            "names": ["매입채무", "유동매입채무", "매입채무및기타채무"],
            "ids": [
                "ifrs-full_TradeAndOtherCurrentPayables",
                "dart_ShortTermTradePayables",
                "ifrs-full_TradeAndOtherPayablesToTradeSuppliers",
                "ifrs-full_TradeAndOtherCurrentPayablesToTradeSuppliers",
            ],
        }

    if account == BalanceSheetAccounts.SHORT_TERM_BORROWINGS:
        return {
            "names": [
                "유동성장기차입금",
                "단기차입금",
                "단기차입금 및 유동성장기부채",
                "단기차입금및유동성장기차입금",
                "외화단기차입금",
                "단기 차입금",
                "차입금",
                "유동 장기 차입금",
                "유동성 단기차입금",
                "차입금및사채",
                "유동성사채및장기차입금",
                "유동차입금및유동사채",
                "유동 차입금 및 사채",
                "유동성차입금",
                "유동차입금",
            ],
            "ids": [
                "ifrs-full_ShorttermBorrowings",
                "ifrs-full_Borrowings",
                "ifrs-full_OtherCurrentFinancialLiabilities",
            ],
        }
    if account == BalanceSheetAccounts.CURRENT_CONVERTIBLE_BONDS:
        return {
            "names": ["전환사채", "전환사채(유동)", "유동전환사채"],
            "ids": ["dart_CurrentPortionOfConvertibleBonds", "dart_ConvertibleBonds"],
        }
    if account == BalanceSheetAccounts.SHORT_TERM_INCOME_RECEIVED_IN_ADVANCE:
        return {
            "names": ["선수수익(유동)"],
            "ids": ["dart_ShortTermIncomeReceivedInAdvance"],
        }
    if account == BalanceSheetAccounts.SHORT_TERM_ADVANCES_CUSTOMERS:
        return {
            "names": ["선수금(유동)"],
            "ids": ["dart_ShortTermAdvancesCustomers", "ifrs-full_Advances"],
        }

    if account == BalanceSheetAccounts.NON_CURRENT_LIABILITIES:
        return {"names": ["비유동부채"], "ids": ["ifrs-full_NoncurrentLiabilities"]}
    if account == BalanceSheetAccounts.TRADE_AND_OTHER_NON_CURRENT_PAYABLES:
        return {
            "names": [
                "비유동매입채무 및 기타채무",
                "장기매입채무 및 기타채무",
                "매입채무 및 기타금융부채(비유동)",
                "장기매입채무및기타채무",
            ],
            "ids": [
                "dart_LongTermTradeAndOtherNonCurrentPayables",
                "dart_LongTermTradePayablesGross",
            ],
        }
    if account == BalanceSheetAccounts.LONG_TERM_BORROWINGS:
        return {
            "names": [
                "장기차입금 및 사채",
                "장기차입금",
                "비유동차입금및비유동사채",
                "비유동차입금",
            ],
            "ids": ["dart_LongTermBorrowingsGross", "ifrs-full_LongtermBorrowings"],
        }
    if account == BalanceSheetAccounts.NON_CURRENT_CONVERTIBLE_BONDS:
        return {"names": ["비유동전환사채", "전환사채(장기)"], "ids": []}
    if account == BalanceSheetAccounts.LONG_TERM_INCOME_RECEIVED_IN_ADVANCE:
        return {
            "names": [],
            "ids": ["dart_LongTermIncomeReceivedInAdvance"],
        }
    if account == BalanceSheetAccounts.LONG_TERM_ADVANCES_CUSTOMERS:
        return {"names": ["장기선수금"], "ids": ["dart_LongTermAdvancesCustomers"]}

    if account == BalanceSheetAccounts.EQUITY:
        return {"names": ["자본총계"], "ids": ["ifrs-full_Equity"]}
    if account == BalanceSheetAccounts.RETAINED_EARNINGS:
        return {
            "names": ["이익잉여금", "이익잉여금(결손금)"],
            "ids": ["ifrs-full_RetainedEarnings"],
        }
    if account == BalanceSheetAccounts.ISSUED_CAPITAL:
        return {"names": ["자본금"], "ids": ["ifrs-full_IssuedCapital"]}

    if account == BalanceSheetAccounts.EQUITY_AND_LIABILITIES:
        return {"names": ["자본과부채총계"], "ids": ["ifrs-full_EquityAndLiabilities"]}


def get_cis_account_detail(account: IncomeStatementAccounts):
    if account == IncomeStatementAccounts.REVENUE:
        return {"names": ["매출액"], "ids": ["ifrs-full_Revenue"]}
    if account == IncomeStatementAccounts.REVENUE_FROM_SALE_OF_GOODS_PRODUCT:
        return {
            "names": ["제품매출", "제품매출액"],
            "ids": [
                "dart_RevenueFromSaleOfGoodsProduct",
                "ifrs-full_RevenueFromSaleOfGoods",
            ],
        }
    if account == IncomeStatementAccounts.REVENUE_FROM_SALE_OF_GOODS_MERCHANDISE:
        return {
            "names": ["상품매출", "상품매출액", "(1) 상품매출액"],
            "ids": ["dart_RevenueFromSaleOfGoodsMerchandise"],
        }
    if account == IncomeStatementAccounts.COST_OF_SALES:
        return {"names": ["매출원가"], "ids": ["ifrs-full_CostOfSales"]}
    if account == IncomeStatementAccounts.COST_OF_SALES_FROM_SALE_OF_GOODS_PRODUCT:
        return {
            "names": ["제품매출원가"],
            "ids": ["dart_CostOfSalesFromSaleOfGoodsProduct"],
        }
    if account == IncomeStatementAccounts.COST_OF_SALES_FROM_SALE_OF_GOODS_MERCHANDISE:
        return {
            "names": ["상품매출원가"],
            "ids": [
                "ifrs-full_CostOfMerchandiseSold",
                "dart_CostOfSalesFromSaleOfGoods",
            ],
        }
    if account == IncomeStatementAccounts.GROSS_PROFIT:
        return {"names": ["매출총이익"], "ids": ["ifrs-full_GrossProfit"]}

    if account == IncomeStatementAccounts.SELLING_GENERAL_ADMINISTRATIVE_EXPENSES:
        return {
            "names": ["판매비와관리비", "판매비", "관리비", "판매관리비", "판매비용"],
            "ids": [
                "dart_TotalSellingGeneralAdministrativeExpenses",
                "ifrs-full_GeneralAndAdministrativeExpense",
                "ifrs-full_SellingGeneralAndAdministrativeExpense",
                "ifrs-full_SellingExpense",
            ],
        }

    if account == IncomeStatementAccounts.OPERATING_INCOME_LOSS:
        return {
            "names": ["영업이익"],
            "ids": [
                "dart_OperatingIncomeLoss",
                "ifrs-full_ProfitLossFromOperatingActivities",
            ],
        }
    if account == IncomeStatementAccounts.PROFIT_LOSS:
        return {
            "names": ["당기순이익", "당기순이익(손실)"],
            "ids": ["ifrs-full_ProfitLoss"],
        }


def get_cf_account_detail(account: CashFlowAccounts):
    if account == CashFlowAccounts.OPERATING_ACTIVITIES:
        return {
            "names": ["영업활동현금흐름"],
            "ids": [
                "ifrs-full_CashFlowsFromUsedInOperatingActivities",
                "ifrs-full_CashFlowsFromUsedInOperations",
            ],
        }
    if account == CashFlowAccounts.PROFIT_LOSS:
        return {"names": ["당기순이익"], "ids": ["ifrs-full_ProfitLoss"]}

    # if (
    #     account
    #     == CashFlowAccounts.ADJUSTMENTS_FOR_ASSETS_LIABILITIES_OF_OPERATING_ACTIVITIES
    # ):
    #     return {
    #         "names": [
    #             "영업으로부터 창출된 현금흐름",
    #             "영업에서 창출된 현금",
    #             "영업으로부터창출된현금",
    #             "영업에서 창출한 현금흐름",
    #             "영업활동에서창출된현금흐름",
    #         ],
    #         "ids": [
    #             "dart_NetCashflowsFromUsedInOperations",
    #             "dart_AdjustmentsForAssetsLiabilitiesOfOperatingActivities",
    #             "ifrs-full_OtherInflowsOutflowsOfCashClassifiedAsOperatingActivities",
    #             "ifrs-full_AdjustmentsForReconcileProfitLoss",
    #         ],
    #     }

    if account == CashFlowAccounts.INTEREST_PAID:
        return {
            "names": [
                "이자지급",
                "이자지급액",
                "이자지급(영업)",
            ],
            "ids": [
                "ifrs-full_InterestPaidClassifiedAsOperatingActivities",
                "ifrs-full_InterestPaidClassifiedAsOperatingActivities",
            ],
        }
    if account == CashFlowAccounts.INTEREST_RECEIVED:
        return {
            "names": ["이자수취", "이자수취(영업)", "이자수취액"],
            "ids": ["ifrs-full_InterestReceivedClassifiedAsOperatingActivities"],
        }

    if account == CashFlowAccounts.INVESTING_ACTIVITIES:
        return {
            "names": ["투자활동현그흐름"],
            "ids": ["ifrs-full_CashFlowsFromUsedInInvestingActivities"],
        }
    if account == CashFlowAccounts.PURCHASE_OF_FINANCIAL_INSTRUMENTS:
        return {
            "names": [
                "단기금융상품의 증가",
                "단기금융상품의 취득",
                "장단기금융상품의 취득",
                "금융상품의 증가",
                "장기금융상품의 납입",
                "장기금융상품의증가",
                "장단기금융상품의 증가",
                "장ㆍ단기금융상품의 증가",
                "장,단기금융상품의 증가",
            ],
            "ids": [
                "dart_PurchaseOfShortTermFinancialInstruments",
                "dart_PurchaseOfLongTermFinancialInstruments",
                "dart_PurchaseOfFinancialInstruments",
                "ifrs-full_PurchaseOfFinancialInstrumentsClassifiedAsInvestingActivities",
                "ifrs-full_PurchaseOfOtherLongtermAssetsClassifiedAsInvestingActivities",
            ],
        }
    if account == CashFlowAccounts.SALES_OF_FINANCIAL_INSTRUMENTS:
        return {
            "names": [
                "단기금융상품의 감소",
                "장기금융상품의처분",
                "장기금융상품의 감소",
                "장단기금융상품의 처분",
                "단기금융상품의 처분",
                "장기금융상품의 해지",
                "단기금융상품의 해지",
                "장기금융상품의감소",
                "단기금융상품의감소",
                "장단기금융상품의 감소",
                "장ㆍ단기금융상품의 감소",
                "장,단기금융상품의 감소",
            ],
            "ids": [
                "dart_ProceedsFromSalesOfShortTermFinancialInstruments",
                "dart_ProceedsFromSalesOfLongTermFinancialInstruments",
                "dart_ProceedsFromSalesOfFinancialInstruments",
                "dart_ProceedsFromSalesOfOtherFinancialAssets",
                "dart_ProceedsFromSalesOfOtherCurrentFinancialAssets",
            ],
        }

    if account == CashFlowAccounts.PURCHASE_OF_PROPERTY_PLANT_AND_EQUIPMENT:
        return {
            "names": [
                "유형자산의 취득",
                "유형자산의취득",
                "유형자산의 증가",
                "유형자산 취득",
            ],
            "ids": [
                "ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
                "dart_PurchaseOfOtherPropertyPlantAndEquipment",
            ],
        }
    if account == CashFlowAccounts.SALES_OF_PROPERTY_PLANT_AND_EQUIPMENT:
        return {
            "names": [
                "유형자산의 처분",
                "유형자산의 감소",
                "유형자산 처분",
                "유형자산 감소",
            ],
            "ids": [
                "ifrs-full_ProceedsFromSalesOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
            ],
        }

    if account == CashFlowAccounts.FINANCING_ACTIVITIES:
        return {
            "names": ["재무활동현금흐름"],
            "ids": ["ifrs-full_CashFlowsFromUsedInFinancingActivities"],
        }

    if account == CashFlowAccounts.PROCEEDS_FROM_BORROWINGS:
        return {
            "names": [
                "차입금의 증가",
                "단기차입금의 차입",
                "장기차입금의 차입",
                "장기차입금의 증가",
                "단기차입금의 증가",
                "차입금의 순차입",
                "단기차입금의차입",
                "장기차입금의차입",
                "단기차입금의 순증감",
                "장기차입금의 증감",
                "차입금의 차입",
                "단기차입금의 순차입",
                "장기차입금의 순차입",
                "차입금및사채의 증가",
                "장기차입금 및 사채의 차입",
                "사채 및 장기차입금 차입",
                "단기차입금의증가",
                "유동성장기차입금의 차입",
                "유동성장기차입금의 증가",
                "장기차입금 차입",
                "단기차입금 증가",
                "차입금 차입",
                "유동성장기부채및단기차입금의 차입",
                "장기차입금의증가",
                "단기차입금 및 사채의 차입",
                "유동성차입금의 증가",
                "차입금 및 사채의 차입",
            ],
            "ids": [
                "dart_ProceedsFromShortTermBorrowings",
                "dart_ProceedsFromLongTermBorrowings",
                "ifrs-full_ProceedsFromBorrowingsClassifiedAsFinancingActivities",
                "ifrs-full_ProceedsFromNoncurrentBorrowings",
                "ifrs-full_ProceedsFromCurrentBorrowings",
            ],
        }
    if account == CashFlowAccounts.REPAYMENTS_OF_BORROWINGS:
        return {
            "names": [
                "유동성장기차입금의 상환",
                "장기차입금의 상환",
                "단기차입금의 상환",
                "유동성장기차입금의 감소",
                "장기차입금의 감소",
                "단기차입금의 감소",
                "유동장기차입금의 상환",
                "차입금의 상환",
                "차입금의 감소",
                "차입금의 순상환",
                "유동성장기차입금의상환",
                "유동성 장기차입금의 상환",
                "(유동성)장기차입금 상환",
                "유동성장기차입금 상환",
                "장기차입금의상환",
                "단기차입금의상환",
                "유동차입금의 상환",
                "장기차입금 상환",
                "차입금및사채의 상환",
                "유동성차입금의 상환",
                "장기차입금 및 사채의 상환",
                "사채 및 장기차입금 상환",
                "단기차입금의 순상환",
                "차입금 상환",
                "유동성단기차입금의 상환",
                "단기차입금의감소",
                "단기차입금 감소",
                "유동성장기부채및단기차입금의 상환",
                "유동성 장기차입금의 감소",
                "유동성장차입금의 감소",
                "단기차입금 및 사채의 상환",
                "유동성차입금(기타)의 상환",
                "유동성차입금의 감소",
                "유동성자기차입금 상환",
                "장기차입금 감소",
                "유동성장기차입금의감소",
            ],
            "ids": [
                "dart_RepaymentsOfLongTermBorrowings",
                "dart_RepaymentsOfShortTermBorrowings",
                "ifrs-full_RepaymentsOfBorrowingsClassifiedAsFinancingActivities",
                "ifrs-full_RepaymentsOfCurrentBorrowings",
                "ifrs-full_RepaymentsOfNoncurrentBorrowings",
            ],
        }

    if account == CashFlowAccounts.DIVIDENDS_PAID:
        return {
            "names": ["배당금지급", "배당금의 지급"],
            "ids": ["ifrs-full_DividendsPaidClassifiedAsFinancingActivities"],
        }
