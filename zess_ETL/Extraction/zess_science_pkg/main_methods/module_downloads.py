import wget
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def download_file(url, dir):
    fn = wget.download(url, out=dir)
    print(f'Finished downloading file {fn}')
    return fn
