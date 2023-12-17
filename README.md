# Report Path Fetcher App
## Overview
A Python Application that fetches the report paths from IBM Cognos Content Store.

## Running the App
### Prerequisites
- [Python](https://www.python.org/downloads/)
### Execution
- Create a Virtual Environment **python -m venv .venv**
- Activate the Virtual Environment **.venv\Scripts\Activate.ps1**
- Install the required libraries **pip install -r requirements.txt"**
- Run the application **python app.py**
- The application prompts the user for the COGNOS Namespace, Username, Password and the base url (`http://<cognos_analytics_server>:<port>`)
- Once the user is authenticated the reports are fetched from the Cognos Content Store.
- The user is then prompted to enter the Folder to fetch Reports from or "all" to fetch all reports.
- The Application generates an excel file with the Report Names and Paths of all the reports in the folder.