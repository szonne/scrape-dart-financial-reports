# scrape-dart-financial-reports

OPENDART API를 활용, 사업보고서 데이터 불러오기

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