import os

from mediqbox.download import *

input_data = DownloadInputData(urls=[
  "https://freetestdata.com/wp-content/uploads/2022/02/Free_Test_Data_1MB_MP4.mp4",
  "https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_1MB_MP3.mp3",
  "https://freetestdata.com/wp-content/uploads/2021/09/Free_Test_Data_1MB_PDF.pdf",
  "https://freetestdata.com/wp-content/uploads/2021/09/png-1mb.png",
  "https://freetestdata.com/wp-content/uploads/2023/04/2.4KB_JSON-File_FreeTestData.json",
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