<!-- To preview markdown in vscode in MAC: press CMD + Shift + V  . This helps in editing markdown-->
# Data Analytics - SA Community

This repository will contain the codes for data analysis for sacommunity

1. Create Python Virtual Environment. Let's name it .venv
Reference: https://docs.python.org/3/library/venv.html

2. create command
python -m venv .venv

3. activate the virtual environment
source .venv/bin/activate

4. install dependencies from requirements.txt
pip install -r requirements.txt

## Project Settings
1. Copy settings/app_settings_sample.json and rename it to app_settings.json
2. Add value for ViewId_V4 property. Login to google analytics (https://analytics.google.com/). In the "Analytics Accounts" menu, the integer number below the website url is the viewId.
3. (Optional) Download the service account credentials from teams folder if you want to use existing service account. Alternatively, you can follow the following procedures to create your own Authentication mechanism. Save this file with the name service_account.json in credentials folder.
3. Copy env_sample file and name it .env
    This file contains the environment variables. Eg. GOOGLE_APPLICATION_CREDENTIALS is the file path for the service account

If you want to use your own credentials, then read details on docs/google-analytics-authentication.md


## Coding Convention
1. pylint
https://pylint.readthedocs.io/en/stable/

    check warnings from pylint with following command (do not supress warning from pylint unless necessary, resolve as many warnings as possible)
```
    pylint $(git ls-files '*.py')
```

2. Run unit tests
```
    python -m unittest discover -s ./tests/helpers -p "*_tests.py"
```
3. Logging (File based)
https://docs.python.org/3/library/logging.html

    Persistent logging enables to go through the error messages to debug. We are storing logs in file in logs folder

## Features of the project
1. Get data from Google Analytics 4 API filtered by datasetId.
    1. Refer [google_analytics_service_tests.ipynb](google_analytics_service_tests.ipynb) for sessions data retrieval. 
    2. Refer [landing_page.ipynb](landing_page.ipynb) for session data based on landing page and data cleaning.
### For the following features, the data source is the cu_export data from [sacommunity.org/export](https://sacommunity.org/export). 
Select Data.Gov.au export as profile. Select the council for export.

2. Get data from Google Analytics 4 API filtered by organisationId. The organisation ids are retrieved from cu_export data. Refer [google_analytics_service_tests.ipynb](google_analytics_service_tests.ipynb) to check sessions data retrieval from organisation ids. The code are at the bottom of the notebook. 
3. Scrape council name from organisation's address. The addresses are retrieved from cu_export data.
    1. Refer [find-council.ipynb](find-council.ipynb) for code usage.
    2. Refer [scraped-council-analysis.ipynb](scraped-council-analysis.ipynb) for analysis of scraped council name
4. Check broken links in the website. The source of urls for organisation is the cu_export data.
    1. Refer [url_checker_tests.ipynb](url_checker_tests.ipynb) for code invocation.

## Future Plan - Roadmap (TODO)
1. Create API for all the operations.
2. Implement CI/CD to deploy the app in AWS
    Github Actions
    Terraform
    S3 to store the files
    DynamoDB or PostgreSQL as database

