from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

from .metadata import MetadataField

metadata_definition_file = "metadata_definitions.tsv"

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test_definition/")
def get_metadata_definition():
    metadata = MetadataField.read_definition(metadata_definition_file)
    return {"metadata_fields": metadata}