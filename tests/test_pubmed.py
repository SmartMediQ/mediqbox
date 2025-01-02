import json
import os

from mediqbox.pubmed import *
from tests import data_dir

with open(os.path.join(data_dir, "mixed.json"), "r") as f:
  test_data = json.load(f).get("pubmed")

def test_pubmed():
  config = PubmedConfig(
    ncbi_email=os.getenv("NCBI_EMAIL"),
    ncbi_api_key=os.getenv("NCBI_API_KEY"),
  )
  pubmed = Pubmed(config)
  
  for data in test_data:
    input_data = PubmedInputData(
      query=data.get("query"),
      pmid_only=data.get("pmid_only", False),
    )
    result: PubmedResult = pubmed.process(input_data)
    print(f"input data: {input_data}")
    assert result.status == "done"
    assert len(result.records) == result.retmax
    
    if data.get("max_results", 0) == 1:
      assert result.count == 1
      assert result.retmax == 1
      assert len(result.records) == 1
      assert result.records[0].pmid
    
    if data.get("doi", False):
      assert result.records[0].doi == data.get("doi")
      
    if data.get("pub_types", False):
      print(f"pub types: {result.records[0].pub_types}")
      assert set(result.records[0].pub_types) >= set(data.get("pub_types"))
    
    if data.get("pmid_only", False):
      records = [record.model_dump(mode="json", exclude_none=True) for record in result.records]
      print(f"records: {records}")
      assert all(len(r) == 1 and "pmid" in r for r in records)