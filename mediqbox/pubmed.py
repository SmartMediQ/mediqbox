from Bio import Entrez, Medline
from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Optional
from typing_extensions import Self

from .abc import *

class PubmedConfig(ComponentConfig):
  ncbi_email: str = Field(
    ...,
    description="The email address to use for PubMed API.",
  )
  ncbi_api_key: str = Field(
    ...,
    description="The API key to use for PubMed API.",
  )
  
class PubmedInputData(InputData):
  query: str = Field(
    ...,
    description="The query string to search PubMed.",
  )
  max_results: int = Field(
    ge=1,
    default=10,
    description="The maximum number of results to return.",
  )
  sort: Literal["relevance", "pub_date"] = Field(
    "relevance",
    description="The sort order of results.",
  )
  pmid_only: bool = Field(
    False,
    description="Return only PMIDs.",
  )
  
class PubmedRecord(BaseModel):
  pmid: str = Field(
    ...,
    description="The unique identifier of the PubMed record.",
  )
  pmcid: Optional[str] = Field(
    None,
    description="The unique identifier of the PubMed Central record.",
  )
  doi: Optional[str] = Field(
    None,
    description="The DOI of the PubMed record.",
  )
  source: Optional[str] = Field(
    None,
    description="The source of the PubMed record.",
  )
  journal: Optional[str] = Field(
    None,
    description="The journal of the PubMed record.",
  )
  issn: Optional[str] = Field(
    None,
    description="The ISSN of the PubMed record.",
  )
  pub_date: Optional[str] = Field(
    None,
    description="The publication date of the PubMed record.",
  )
  title: Optional[str] = Field(
    None,
    description="The title of the PubMed record.",
  )
  abstract: Optional[str] = Field(
    None,
    description="The abstract of the PubMed record.",
  )
  authors: Optional[List[str]] = Field(
    None,
    description="The authors of the PubMed record.",
  )
  keywords: Optional[List[str]] = Field(
    None,
    description="The keywords of the PubMed record.",
  )
  pub_types: Optional[List[str]] = Field(
    None,
    description="The publication types of the PubMed record.",
  )
  languages: Optional[List[str]] = Field(
    None,
    description="The languages of the PubMed record.",
  )
  
  @model_validator(mode="after")
  def extract_doi(self) -> Self:
    if self.source and "doi: " in self.source:
      self.doi = self.source.split("doi: ")[1]
      if " " in self.doi:
        self.doi = self.doi.split(". ")[0]
      else:
        self.doi = self.doi[:-1] # Remove the period
    return self
  
class PubmedResult(OutputResult):
  count: int = Field(
    ...,
    description="The total number of PubMed records.",
  )
  retmax: int = Field(
    ...,
    description="The number of PubMed records returned.",
  )
  records: List[PubmedRecord] = Field(
    default=[],
    description="The list of PubMed records.",
  )
  
class Pubmed(AbstractComponent):
  def _process(self, data: PubmedInputData) -> PubmedResult:
    config: PubmedConfig = self.config
    Entrez.email = config.ncbi_email
    Entrez.api_key = config.ncbi_api_key
    
    handle = None
    try:
      handle = Entrez.esearch(
        db="pubmed",
        term=data.query,
        retmax=data.max_results,
        sort=data.sort,
      )
      search_record = Entrez.read(handle)
      pmids = search_record["IdList"]
    except Exception as e:
      self.logger.exception(e)
      raise e
    finally:
      if handle:
        handle.close()
        
    if data.pmid_only:
      return PubmedResult(
        count=int(search_record["Count"]),
        retmax=len(pmids),
        records=[PubmedRecord(pmid=pmid) for pmid in pmids],
      )
    
    result = PubmedResult(
      count=int(search_record["Count"]),
      retmax=int(search_record["RetMax"]),
      records=[],
    )
    
    handle = None
    try:
      handle = Entrez.efetch(
        db="pubmed",
        id=pmids,
        rettype="medline",
        retmode="text",
      )
      fetch_records = Medline.parse(handle)
      
      for record in fetch_records:
        result.records.append(PubmedRecord(
          pmid=record.get("PMID", ""),
          pmcid=record.get("PMC", ""),
          source=record.get("SO", ""),
          journal=record.get("JT", ""),
          issn=record.get("IS", ""),
          pub_date=record.get("DP", ""),
          title=record.get("TI", ""),
          abstract=record.get("AB", ""),
          authors=record.get("AU", []),
          keywords=record.get("OT", []),
          pub_types=record.get("PT", []),
          languages=record.get("LA", []),
        ))
      
      return result
    except Exception as e:
      self.logger.exception(e)
      raise e
    finally:
      if handle:
        handle.close()