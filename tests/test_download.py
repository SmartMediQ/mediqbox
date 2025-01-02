import json
import os

from mediqbox.download import *
from tests import data_dir

output_dir = os.path.join(os.path.dirname(__file__), "output")

with open(os.path.join(data_dir, "mixed.json"), "r") as f:
  download_urls = json.load(f).get("download_urls")
  input_data = DownloadInputData(urls=download_urls)

def test_download():
  # Remove files in target_dir
  for item in os.listdir(output_dir):
    fullpath = os.path.join(output_dir, item)
    if os.path.isfile(fullpath):
      os.unlink(fullpath)
      
  config = DownloadConfig(
    output_dir=output_dir,
    max_concurrency=2,
  )
  downloader = Downloader(config)
  result = downloader.process(input_data)
  assert result.status == "done"
  assert len(result.downloaded_files) == len(input_data.urls)
  for url, file in zip(input_data.urls, result.downloaded_files):
    print(f"Downloaded {url} to {file}")
    assert os.path.exists(file)
    assert os.path.getsize(file) > 0