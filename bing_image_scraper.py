import requests
import re
import shutil
import urllib
from pathlib import Path
import posixpath

class BingImageScraper:

  def __init__(self):
    self.base_url = 'https://www.bing.com/images/async'
    self.headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'
    }
    self.timeout = 60

  @staticmethod
  def get_file_name(query):
    return '_'.join(query.lower().split())

  def download_image(self, image_url, file_path):
    path = urllib.parse.urlsplit(image_url).path
    filename = posixpath.basename(path).split('?')[0]
    file_type = filename.split('.')[-1]
    if file_type.lower() not in ['jpe', 'jpeg', 'jfif', 'exif', 'tiff', 'gif', 'bmp', 'png', 'webp', 'jpg']:
        file_type = 'jpg'
    file_path = f'{file_path}.{file_type.lower()}'
    try:
      response = requests.get(image_url, headers=self.headers, stream=True, timeout=self.timeout)
      if response.status_code == 200:
          with open(file_path, 'wb') as f:
              response.raw.decode_content = True
              shutil.copyfileobj(response.raw, f)
              return True
      return False
    except Exception as e:
      print(f'  !! Error downloading image from {image_url}')
      return False

  def search(self, query, limit, adult_filter_on, output_dir):
    file_name = self.get_file_name(query)
    adult_filter = 'on' if adult_filter_on else 'off'
    page_count = 0
    download_count = 0
    while download_count < limit:
      url = f'{self.base_url}?q={query}&first={page_count}&count={limit}&adlt={adult_filter}'
      response = requests.get(url, headers=self.headers, timeout=self.timeout)
      links = re.findall('murl&quot;:&quot;(.*?)&quot;', response.text)
      for link in links:
        if download_count < limit:
          print(f'  >> Downloading image #{download_count} from {link}')
          file_path = output_dir.joinpath(f'{file_name}_{download_count}')
          success = self.download_image(link, file_path)
          if success:
            download_count += 1
      page_count += 1

  def start(self, query, limit, adult_filter_on=True, output_dir='data', overwrite=False):
    print(f'>> Downloading {limit} images for query "{query}"')
    sub_dir = self.get_file_name(query)
    output_dir = Path(output_dir).joinpath(sub_dir).absolute()
    if overwrite:
        if Path.isdir(output_dir):
            shutil.rmtree(output_dir)
    if not Path.is_dir(output_dir):
        Path.mkdir(output_dir, parents=True)
    self.search(query, limit, adult_filter_on, output_dir)
