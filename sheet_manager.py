import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scraper import WebScraper
from scraper_headless import WebScraperHeadless
import validators
from googleapiclient.discovery import build  # Import this library to interact with the Google Drive API

class SheetManager:
    def __init__(self, credentials_path, headless=False):
        self.credentials_path = credentials_path
        self.headless = headless
        self.client = self.authenticate()

    def authenticate(self):
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        self.drive_service = build('drive', 'v3', credentials=creds)
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
        sheet_data = self.necessary_ranges(sheet)

        target_url = sheet_data['target_url']
        urls = sheet_data['urls']
        colds = sheet_data['col_d']
        stop_row = sheet_data['last_row']

        total_rows = len(urls) + 10 # Calculate the total number of rows based on urls
        # Choose the scraper based on the headless flag
        if self.headless:
            scraper = WebScraperHeadless(target_url)
        else:
            scraper = WebScraper(target_url)
        results = []
        extra_info = []
        follow_nofollow = []
        for index, (url, cold) in enumerate(zip(urls, colds), start=11):
            if validators.url(url) and (cold == "TRUE"):
                url = url.strip()
                print(f"checking {url}", end=" ", flush=True)
                try:
                    result, follow, nofollow = scraper.find_urls(url)
                    # if (result == 'not found') or (result == 'error'):
                    #     extra_info.append((index, result))    
                    # else:
                    #     results.append((index, result))
                    results.append((index, result))
                    print(result, end="", flush=True)
                    if follow is not None:
                        follow_nofollow.append((index, follow, nofollow))
                except Exception as e:
                    print(f"failed to fetch for this {url} from {spreadsheet_id}")    
                print("")
            else:
                results.append((index, ""))
            # if index == stop_row: break
        scraper.close_driver()

        # Perform batch updates using the batch_update_sheet function
        self.batch_update_sheet(sheet, results, follow_nofollow, extra_info)

    def batch_update_sheet(self, sheet, results, follow_nofollow, extra_info):
        # Prepare a list of cell updates
        cell_list = []

        # Update results for columns T and U
        for res in results:
            cell_list.append(gspread.Cell(res[0], 10, res[1]))  # Column J is the 10th column
            #cell_list.append(gspread.Cell(res[0], 21, res[2]))  # Column U is the 21st column

        # Update follow/nofollow for columns O and P
        for fn in follow_nofollow:
            cell_list.append(gspread.Cell(fn[0], 15, fn[1]))  # Column O is the 15th column
            cell_list.append(gspread.Cell(fn[0], 16, fn[2]))  # Column P is the 16th column
        
        # Update extra info whether error occured or not found in column U 21st Column
        # for ei in extra_info:
        #     cell_list.append(gspread.Cell(ei[0], 21, ei[1]))  # Column U is the 21st column

        # Perform the batch update
        sheet.update_cells(cell_list, value_input_option='USER_ENTERED')
    
    def necessary_ranges(self, sheet):
        range_list = ["F9", "D11:D", "G11:G"]
        data_set = sheet.batch_get(range_list)
        sheet_data = {}
        sheet_data['target_url'] = data_set[0][0][0]
        sheet_data['col_d'] = [item[0] if item else "" for item in data_set[1]]
        sheet_data['urls'] = [item[0] if item else "" for item in data_set[2]]
        for index in range(len(sheet_data['col_d']) - 1, -1, -1):
            if sheet_data['col_d'][index].lower() == 'true':
                last_row = index + 1 + 10
                break  # +1 to convert from 0-based index to 1-based index
    
        sheet_data['last_row'] = last_row
        return sheet_data

# execute
# execute
if __name__ == '__main__':
    manager = SheetManager('./urlvalidate.json', headless=True)
    folder_id = '1iEZd2BUKInMv4zi4ZrrSqKLfMCU8rbRI'  # Replace this with your actual Google Drive folder ID
    spreadsheets = manager.list_spreadsheets_in_folder(folder_id)
    for spreadsheet in spreadsheets:
        # Check if the first character of the name is a digit
        if spreadsheet['name'][0].isdigit():
            print(f"Skipping {spreadsheet['name']} as it starts with a number.")
            continue
        print(f"Processing {spreadsheet['name']} with ID {spreadsheet['id']}")
        try:
            manager.process_sheet(spreadsheet['id'])
        except Exception as e:
            print(f"couldn't process file: {spreadsheet['name']} due to error {e}")
