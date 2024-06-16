import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scraper import WebScraper
import validators
from googleapiclient.discovery import build  # Import this library to interact with the Google Drive API

class SheetManager:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.client = self.authenticate()

    def authenticate(self):
        # Add the Google Drive scope along with the Google Sheets scope
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        self.drive_service = build('drive', 'v3', credentials=creds)  # Build the Drive API service
        return gspread.authorize(creds)

    def list_spreadsheets_in_folder(self, folder_id):
        # List all files in the specified folder that are Google Sheets
        results = self.drive_service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name)").execute()
        items = results.get('files', [])
        return items  # Returns a list of files represented as dictionaries

    def process_sheet(self, spreadsheet_id):
        sheet = self.client.open_by_key(spreadsheet_id).worksheet("Saisie")
        target_url = sheet.acell('F9').value
        urls = sheet.col_values(7)[10:]  # Assuming G9 is the header
        total_rows = len(urls) + 10  # Calculate the total number of rows based on urls

        scraper = WebScraper(target_url)
        results = []
        extra_info = []
        follow_nofollow = []
        for index, url in enumerate(urls, start=11):
            if validators.url(url):
                result, follow, nofollow = scraper.find_urls(url)
                if (result == 'not found') or (result == 'error'):
                    extra_info.append((index, result)) 
                    
                else:
                    results.append((index, result))
                
                if follow is not None:
                    follow_nofollow.append((index, follow, nofollow))

        scraper.close_driver()

        # Perform batch updates using the batch_update_sheet function
        self.batch_update_sheet(sheet, results, follow_nofollow, extra_info)

    def batch_update_sheet(self, sheet, results, follow_nofollow, extra_info):
        # Prepare a list of cell updates
        cell_list = []

        # Update results for columns T and U
        for res in results:
            cell_list.append(gspread.Cell(res[0], 20, res[1]))  # Column T is the 20th column
            #cell_list.append(gspread.Cell(res[0], 21, res[2]))  # Column U is the 21st column

        # Update follow/nofollow for columns O and P
        for fn in follow_nofollow:
            cell_list.append(gspread.Cell(fn[0], 15, fn[1]))  # Column O is the 15th column
            cell_list.append(gspread.Cell(fn[0], 16, fn[2]))  # Column P is the 16th column
        
        # Update extra info whether error occured or not found in column U 21st Column
        for ei in extra_info:
            cell_list.append(gspread.Cell(ei[0], 21, ei[1]))  # Column U is the 21st column

        # Perform the batch update
        sheet.update_cells(cell_list, value_input_option='USER_ENTERED')


# execute
if __name__ == '__main__':
    manager = SheetManager('./urlvalidate.json')
    folder_id = '1O1ra-H3a3fOcwFp3vt_0BqcAky4tYHz1'  # You must replace this with your actual Google Drive folder ID
    spreadsheets = manager.list_spreadsheets_in_folder(folder_id)
    for spreadsheet in spreadsheets:
        print(f"Processing {spreadsheet['name']} with ID {spreadsheet['id']}")
        manager.process_sheet(spreadsheet['id'])
