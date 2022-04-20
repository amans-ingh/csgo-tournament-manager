from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

SECRET_KEY = 'some_secret_key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Currently, using SQLite
SERVER_URL = 'https://cargo.win'
STEAM_API_KEY = 'steam_api_key'
SQLALCHEMY_TRACK_MODIFICATIONS = True
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = 'Google_ReCAPTCHA_SITE_KEY'
RECAPTCHA_PRIVATE_KEY = 'Google_ReCAPTCHA_SECRET_KEY'
RECAPTCHA_OPTIONS = {'theme': 'dark'}
SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url="sqlite:///jobstore.db")}
SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 20}}
SCHEDULER_JOB_DEFAULTS = {"coalesce": False, "max_instances": 3}
SCHEDULER_API_ENABLED = False