import logging
import time

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Literal, Optional, Type

class PartialColorFormatter(logging.Formatter):
  # Define ANSI escape codes for colors
  COLORS = {
    "ERROR": "\033[91m",
    "WARNING": "\033[93m",
    "CRITICAL": "\033[95m",
    "RESET": "\033[0m",
  }
  
  def format(self, record):
    if record.levelname in ["WARNING", "ERROR", "CRITICAL"]:
      # Colorize the level name
      record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
      
    return super().format(record)

class ComponentConfig(BaseModel):
  ...
    
class InputData(BaseModel):
  ...
  
class DoNotRetry(Exception):
  """Custom exception to indicate that the process should not be retried."""
  ...
  
class OutputResult(BaseModel):  
  status: Literal["done", "failed"] = "done"
  error_message: Optional[str] = None
  
class AbstractComponent(ABC):
  def __init__(self, config: Type[ComponentConfig]):
    self._config = config
    self._classname = type(self).__name__
    self._logger = logging.getLogger(self._classname)
    
    # Default logger config
    self._logger.setLevel(logging.INFO)
    handler = logging.StreamHandler() # console handler
    formatter = PartialColorFormatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    self._logger.addHandler(handler)
    
  @property
  def config(self):
    return self._config
  
  @property
  def classname(self):
    return self._classname
  
  @property
  def logger(self):
    return self._logger
  
  @abstractmethod
  def _process(self, data: Type[InputData]) -> Optional[Type[OutputResult]]:
    pass
  
  def process(
    self,
    data: Type[InputData],
    max_retries: int=3,
    backoff_factor: float=1.0,
  ) -> Optional[Type[OutputResult]]:
    retries = 0
    
    while retries <= max_retries:
      try:
        return self._process(data)
      except DoNotRetry as e:
        self.logger.error(str(e))
        return OutputResult(status="failed", error_message=str(e))
      except Exception as e:
        retries += 1
        interval = backoff_factor * (2 ** (retries - 1))
        self.logger.error(f"{self.classname} failed: {e}")
        self.logger.info(f"Retrying {self.classname} in {interval} seconds...")
        time.sleep(interval)
        
    return OutputResult(status="failed", error_message="Max retries reached.")