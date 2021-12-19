import os
from datetime import datetime, date, timedelta
from zipfile import ZipFile
from urllib.request import urlretrieve
from urllib.error import HTTPError
from google.cloud import storage

# Config
URL_BASE = "http://www.portaltransparencia.gov.br/download-de-dados/bolsa-familia-pagamentos/"
DATA_DIR = "/home/rodolfo/Downloads/"
JSON_PATH = "/home/rodolfo/Downloads/tvg-bd-governo-c1d99c355641.json"
BUCKET_NAME = "governo-brt-gdata-globo"
PREFIX = "transparencia/bolsa_familia/"
now = date.today()


# Functions
def retrieve_list():
    '''
    Searches our bucket to retrieve a list of raw data we already own
    and returns the last file.
    '''
    global last_file
    storage_client = storage.Client.from_service_account_json(JSON_PATH)
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=PREFIX)
    files = []
    for blob in blobs:
        if blob.name.endswith('Pagamentos.csv'):
            files.append(blob.name)
    files = ' '.join(files).replace('transparencia/bolsa_familia/', '')\
                           .replace('_BolsaFamilia_Pagamentos.csv', '')\
                           .split()
    last_file = files[-1]


def date_iterator(from_date, to_date):
    '''
    Function to iterate over dates.
    '''
    if from_date > to_date:
        return
    else:
        while from_date <= to_date:
            yield from_date
            from_date = from_date + timedelta(days=1)
        return


def create_list():
    '''
    Define the extent of what will be downloaded by setting up the months
    and years of beginning and end.
    '''
    global new_dates
    last_date = date(int(last_file[:4]), int(last_file[4:]), day=1)
    iterobj = date_iterator(last_date, now)
    dates = []
    for i in iterobj:
        x = datetime.strftime(i, '%Y%m')
        dates.append(x)
    new_dates = list(set(dates))


def download_file(url, filename):
    try:
        urlretrieve(url, filename)
        return 1
    except HTTPError:
        print("The url " + url + " could not be accessed")
        return 0


def unzip_file(filename, unziped_dir):
    zip_file = ZipFile(filename, 'r')
    zip_file.extractall(unziped_dir)
    zip_file.close()
    os.remove(filename)


def upload_file_to_gcs(file_path, gcs_path):
    storage_client = storage.Client.from_service_account_json(JSON_PATH)
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(file_path)


def main():
    retrieve_list()
    create_list()
    for i in new_dates:
        url = URL_BASE + 1
        filename = DATA_DIR + "pagamentos" + '_' + i + '.zip'
        if download_file(url, filename) == 0:
            continue
        unziped_dir = DATA_DIR + i + "/"
        unzip_file(filename, unziped_dir)

        unziped_filename = os.listdir(unziped_dir)
        if len(unziped_filename) == 1:
            unziped_filename = unziped_filename[0]
        else:
            print("ERROR: the number of files for this date is wrong")

        gcs_path = "teste/p_date=" + i + "/" + unziped_filename
        file_path = unziped_dir + unziped_filename
        upload_file_to_gcs(file_path, gcs_path)


if __name__ == '__main__':
    main()
