from mediqbox.abc import (
  AbstractComponent,
  ComponentConfig,
  InputData,
  OutputResult,
  DoNotRetry,
)

def test_simple_component():
  class StrInputData(InputData):
    content: str
    
  class SimpleComponent(AbstractComponent):
      
    def _process(self, data: StrInputData) -> OutputResult:
      if not isinstance(data, StrInputData):
        raise DoNotRetry("Invalid input data type!")
      
      self.logger.info(f"Processing data: {data}")
      if not data.content:
        self.logger.warning("Empty content!")
      return OutputResult()
  
  component = SimpleComponent(ComponentConfig())
  data = StrInputData(content="Hello, world!")
  result = component.process(data)
  assert result.status == "done"
  
  data = StrInputData(content="")
  result = component.process(data)
  assert result.status == "done"
  
  data = "Hello, world!"
  result = component.process(data)
  assert result.status == "failed"