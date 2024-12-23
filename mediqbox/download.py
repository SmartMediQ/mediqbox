import aiofiles
import aiohttp
import aiohttp.client_exceptions
import asyncio
import os
import yarl

from collections.abc import Iterable
from pydantic import Field, field_validator
from typing import List, Optional
from urllib.parse import unquote

from .abc import *

class DownloadConfig(ComponentConfig):
  output_dir: str = Field(
    ...,
    description="The directory to save downloaded files.",
  )
  max_concurrency: int = Field(
    ge=1,
    default=5,
    description="The maximum number of concurrent downloads.",
  )
  
  @field_validator("output_dir")
  @classmethod
  def validate_output_dir(cls, value: str):
    if not os.path.exists(value):
      raise ValueError("The output directory does not exist!")
    if not os.path.isdir(value):
      raise ValueError("The output directory is not a directory!")
    if not os.access(value, os.W_OK):
      raise ValueError("The output directory is not writable!")
    return value
  
class DownloadInputData(InputData):
  urls: List[str] = Field(
    ...,
    description="The list of URLs to download.",
  )
  
class DownloadOutputResult(OutputResult):
  downloaded_files: List[str] = Field(
    default=[],
    description="The list of downloaded files.",
  )

class Downloader(AbstractComponent):
  def _process(self, data: DownloadInputData) -> DownloadOutputResult:
    async def download_file(
      session: aiohttp.ClientSession,
      url: str,
    ) -> Optional[str]:
      try:
        async with session.get(yarl.URL(url, encoded=True)) as response:
          response.raise_for_status()
            
          header = response.headers.get("Content-Disposition")
          if header:
            filename = unquote(header.split("filename=")[1])
          else:
            filename = unquote(os.path.basename(url))
              
          if (filename.startswith('"') and filename.endswith('"')) or (filename.startswith("'") and filename.endswith("'")):
            filename = filename[1:-1]
              
          filepath = os.path.join(self.config.output_dir, filename)
          async with aiofiles.open(filepath, "wb") as f:
            await f.write(await response.read())
          return filepath
      except aiohttp.client_exceptions.ClientResponseError as e:
        self.logger.error(f"Failed to download {url}: {e}")
        return None
    
    async def download_files(urls: Iterable[str]) -> List[Optional[str]]:
      connector = aiohttp.TCPConnector(
        limit=self.config.max_concurrency,
        #keepalive_timeout=30,
      )
      async with aiohttp.ClientSession(
        connector=connector,
      ) as session:
        tasks = [download_file(
          session, url
        ) for url in urls]
        return await asyncio.gather(*tasks)
    
    downloaded_files = asyncio.run(download_files(data.urls))
    return DownloadOutputResult(downloaded_files=downloaded_files)