import os

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from pydantic import Field, NameEmail, field_validator
from typing import Any, List, Optional, Protocol, runtime_checkable

from .abc import *

def encode_name_email(name_email: NameEmail) -> str:
  encoded_name = Header(name_email.name, "utf-8").encode()
  return f"{encoded_name} <{name_email.email}>"

def add_attachment(
  msg: MIMEMultipart,
  att: str,
) -> None:
  with open(att, "rb") as f:
    part = MIMEApplication(f.read())
  
  part.add_header(
    "Content-Disposition",
    "attachment",
    filename=Header(os.path.basename(att), "utf-8").encode(),
  )
  msg.attach(part)

@runtime_checkable
class EmailClientProtocol(Protocol):
  def send_raw_email(self, raw_email: bytes) -> None:
    ...

class SendmailConfig(ComponentConfig):
  email_client: Any = Field(
    ...,
    description="The email client to send emails.",
  )
  
  @field_validator("email_client")
  @classmethod
  def validate_email_client(cls, v: Any):
    if not isinstance(v, EmailClientProtocol):
      raise ValueError("The email client must implement send_raw_email method defined by the EmailClientProtocol!")
    return v
  
class SendmailInputData(InputData):
  From: NameEmail = Field(
    ...,
    description="The sender of the email.",
  )
  To: List[NameEmail] = Field(
    ...,
    description="The recipients of the email.",
  )
  Cc: Optional[List[NameEmail]] = Field(
    None,
    description="The CC recipients of the email.",
  )
  Subject: str = Field(
    ...,
    description="The subject of the email.",
  )
  TextBody: str = Field(
    ...,
    description="The text body of the email.",
  )
  HtmlBody: Optional[str] = Field(
    None,
    description="The HTML body of the email.",
  ) 
  Attachments: Optional[List[str]] = Field(
    None,
    description="The list of file paths to attach.",
  )
  
  @field_validator("To")
  @classmethod
  def validate_To(cls, v: List[NameEmail]):
    if not v:
      raise ValueError("The recipients of the email must not be empty!")
    return v
  
  @field_validator("Attachments")
  @classmethod
  def validate_Attachments(cls, v: Optional[List[str]]):
    if v:
      for path in v:
        if not os.path.isfile(path):
          raise ValueError(f"The file path {path} is invalid!")
    return v
  
class SendmailResult(OutputResult):
  pass

class Sendmail(AbstractComponent):
  def _process(
    self,
    data: SendmailInputData
  ) -> SendmailResult:
    config: SendmailConfig = self.config
    
    msg = MIMEMultipart()
    msg["From"] = encode_name_email(data.From)
    msg["To"] = ", ".join([encode_name_email(recipient) for recipient in data.To])
    if data.Cc:
      msg["Cc"] = ", ".join([encode_name_email(recipient) for recipient in data.Cc])
    msg["Subject"] = data.Subject
    
    msg.attach(MIMEText(data.TextBody, "plain", "utf-8"))
    if data.HtmlBody:
      msg.attach(MIMEText(data.HtmlBody, "html", "utf-8"))
      
    if data.Attachments:
      for att in data.Attachments:
        add_attachment(msg, att)
        
    config.email_client.send_raw_email(msg.as_string())
    
    return SendmailResult(status="done")