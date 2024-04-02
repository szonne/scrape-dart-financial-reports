# scrape-dart-financial-reports

OPENDART API를 활용, 사업보고서 데이터 불러오기

### Requirements
1. OPENDART API key 신청 (1~2일 소요)
   - https://opendart.fss.or.kr 접속
   - 인증키 신청/관리 -> 인증키 신청
2. Google colab
   - https://colab.research.google.com 접속
   - '새 노트' 선택
   - 아래의 코드를 복사, 붙여넣기 한 뒤에 셀의 왼쪽에 있는 재생 버튼 클릭
     ```sh
     %%bash
     git clone https://github.com/szonne/scrape-dart-financial-reports
     !python scrape-dart-financial-reports/main.py 
     ``` 
   - 


### Dev setup (Fresh start)
1. Install python 3.10
    - https://www.python.org/downloads/ (other)
    - Installation through brew makes problem between virtualenvwrapper and xcode CLI tool.
2. Create virtualenv with virtualenvwrapper
    1. Install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
    2. Create virtualenv with command follows.
        ```sh
        mkvirtualenv -p python3.10 scrape-dart-finanical-reports
        ```
3. Copy git hooks
    - Check isort, PEP8, black before commit/push
        ```sh
        mkdir -p .git/hooks; cp -a scripts/git/* .git/hooks/
        ```
4. Install packages
    - First time
        - Please match pip and setuptools version one at the Dockerfile
          ```sh
          pip install pip==24.0
          pip install -r requirements.txt
          ```
    - Adding packages
        - production packages: add to requirements.in
        - Run following command to install new package
            ```sh
            pip-compile
            pip-sync
            ```
          
### Usage
```sh
python main.py
```