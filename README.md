# Book Badminton auto
For HK user
to book badminton easily



## how to setup virtual environment

```sh
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
```
## how to run? 
Copy `.env.template` file to `.env` file.
Fill in username and password in .env file
Run command:
```sh
python -m smartplay.main
```
## V2 approach by ding
copy `area_setting.csv.template` to `area_setting.csv`
```sh
python -m smartplay.v2
```
# Limitation
still work in progress, developed in mac platform