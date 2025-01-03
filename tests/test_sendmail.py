import boto3

from typing_extensions import Self

from mediqbox.sendmail import *
from tests import data_dir

class SesEmailClient:
  def __init__(
    self,
    aws_profile_name: str,
  ):
    self._aws_profile_name = aws_profile_name
    
  @property
  def aws_profile_name(self):
    return self._aws_profile_name
  
  def __enter__(self) -> Self:
    session = boto3.Session(profile_name=self.aws_profile_name)
    self._client = session.client("ses")
    return self
  
  def __exit__(self, *_):
    self._client = None
    
  def send_raw_email(self, raw_email: bytes) -> None:
    self._client.send_raw_email(RawMessage={"Data": raw_email})
    
def test_sendmail():
  data = SendmailInputData(
    From=os.getenv("From"),
    To=[os.getenv("To")],
    Cc=[os.getenv("Cc")],
    Subject=os.getenv("Subject"),
    TextBody=os.getenv("TextBody"),
    HtmlBody=os.getenv("HtmlBody"),
    Attachments=[os.path.join(data_dir, item) for item in ["att.txt", "att.pdf"]],
  )
  
  with SesEmailClient(
    aws_profile_name=os.getenv("AWS_PROFILE_NAME"),
  ) as email_client:
    sendmail = Sendmail(config=SendmailConfig(
      email_client=email_client
    ))
    result = sendmail.process(data)
    assert result.status == "done"
    print("Email sent successfully!")