import gspread

from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials


def open_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name( 'client_secret.json', scope)
    client = gspread.authorize(creds)

    spread_sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1YQOnU8UTrYtxxeMW5l57opk5PlyL_UVnrAD-1iwOq6U/edit#gid=343022149"
    )
    google_sheet: Worksheet = spread_sheet.worksheet("DATA")
    data = google_sheet.get_all_values()

    return google_sheet, data
