import os

from mediqbox.download import *

input_data = DownloadInputData(urls=[
  "https://documents.un.org/doc/undoc/ltd/n20/189/21/pdf/n2018921.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-1.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-10.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-100.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-101.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-102.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-103.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-104.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-105.pdf",
  "https://ecosoc.un.org/sites/default/files/documents/2023/resolution-1989-106.pdf",
])

output_dir = os.path.join(os.path.dirname(__file__), "output")

def test_download():
  # Remove files in target_dir
  for item in os.listdir(output_dir):
    fullpath = os.path.join(output_dir, item)
    if os.path.isfile(fullpath):
      os.unlink(fullpath)
      
  config = DownloadConfig(
    output_dir=output_dir,
    #max_concurrency=2,
  )
  downloader = Downloader(config)
  result = downloader.process(input_data)
  assert result.status == "done"
  assert len(result.downloaded_files) == len(input_data.urls)
  for url, file in zip(input_data.urls, result.downloaded_files):
    print(f"Downloaded {url} to {file}")
    assert os.path.exists(file)
    assert os.path.getsize(file) > 0