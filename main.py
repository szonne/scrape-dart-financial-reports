from config import Units
from reports import ReportCalculator

if __name__ == "__main__":

    corp_name = input('회사 이름을 입력하세요: ')
    start_year = int(input('시작 연도를 입력하세요: '))
    end_year = int(input('끝 연도를 입력하세요: '))
    is_connected_num = input('연결재무제표: 1, 별도재무제표: 2\n 숫자를 입력하세요: ')
    if is_connected_num not in ('1', '2'):
        print('적절하지 않은 응답입니다. 별도재무제표 기준으로 데이터를 추출합니다.')
        is_connected_num = '2'

    is_connected = True if is_connected_num == '1' else False
    print(f'{corp_name}의 사업보고서 데이터 취합을 준비 중입니다...')
    report_calculator = ReportCalculator(
        corp_name=corp_name, is_connected=is_connected, unit=Units.THOUSAND
    )

    print(f'{corp_name}의 사업보고서 데이터를 처리 중입니다...')

    report_calculator.write_data(
        start_year=start_year,
        end_year=end_year,
        is_accumulated=True,
    )

    print(f'{corp_name}의 사업보고서 데이터 처리가 완료되었습니다.')

