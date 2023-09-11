import requests
import os
from tqdm import tqdm
from requests.auth import HTTPBasicAuth


def download_file(download_folder, file_url, username=None, password=None):
    filename = file_url.split('/').pop()
    file_path = f'{download_folder}/{filename}'
    chunk_size = 8192

    if username is None:
        response = requests.head(file_url)
    else:
        response = requests.head(file_url, auth=HTTPBasicAuth(username, password))

    file_size = int(response.headers.get('Content-Length', 0))

    if os.path.exists(file_path):
        local_file_size = os.path.getsize(file_path)
    else:
        local_file_size = 0

    while local_file_size < file_size:
        if local_file_size != 0:
            print(f'Downloading missing {100-round((local_file_size/file_size)*100, 2)}% of {filename}')
        header = {'Range': f'bytes={local_file_size}-'}
        if username is None:
            response = requests.get(file_url, headers=header, stream=True)
        else:
            response = requests.get(file_url, headers=header, stream=True, auth=HTTPBasicAuth(username, password))

        with open(file_path, 'ab') as file, tqdm(
                desc=filename,
                total=file_size,
                initial=local_file_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    file.write(chunk)
                    bar.update(len(chunk))

        if os.path.exists(file_path):
            local_file_size = os.path.getsize(file_path)
        else:
            local_file_size = 0


# Example usage

# Get the downloads folder path, for a windows machine
downloads = ''.join(list(os.popen(r'echo %USERPROFILE%\Downloads').read())[:-1])
# This site doesn't have an http password so we don't need these.
username = ''
password = ''

# Download the file. This is just an example file.
download_file(downloads, 'https://bmrf.org/repos/tron/Tron%20v12.0.5%20(2023-02-02).exe')
