from fastapi import APIRouter
from pydantic import BaseModel
from enum import Enum
import json
from jsonschema import validate, ValidationError

router = APIRouter()

# To add Json schema file, update this dictionary and Schema class
json_schema_files = {
#    "dev": "dev_schemas/test_schema.json",
    "ddbj_dev1": "src/dev_schemas/ddbj_submission_dev1.json",
    "minimum": "src/dev_schemas/example_schema_minimum.json",
    "submission_category": "src/dev_schemas/submission_category.json",
    "reference": "src/dev_schemas/reference_schema.json",
    "multi_reference": "src/dev_schemas/reference_schema_multi.json",
    "test": "src/dev_schemas/test.json",
    "ddbj_dev2": "src/templates/ddbj_submission_dev2.json",
}

class Schema(str, Enum):
    # DEV = 'dev'
    DEV1 = 'ddbj_dev1'
    MINIMUM = 'minimum'
    CATEGORY = 'submission_category'
    REFERENCE = 'reference'
    REFERENC2 = "multi_reference"
    TEST = "test"
    DEV2 = "ddbj_dev2"

class SchemaType(BaseModel):
    name: Schema = Schema.MINIMUM

class SchemaValidate(BaseModel):
    name: str = "minimum"
    data: dict

@router.get("/dev/get_schema_types")
async def get_schema_types():
    print(SchemaType.model_json_schema())
    return SchemaType.model_json_schema()

@router.post("/dev/schema", tags=["dev"])
async def get_schema(schema_type: SchemaType):
    json_schema_file = json_schema_files[schema_type.name]
    # print(schema_type)
    # print(schema_type.name)
    with open(json_schema_file) as f:
        example_schema = json.load(f)
    # print(schema_type.model_json_schema())
    return example_schema

@router.post("/dev/validate", tags=["dev"])
async def validate_schema(sc: SchemaValidate):
    json_schema_file = json_schema_files[sc.name]
    with open(json_schema_file) as f:
        example_schema = json.load(f)
    try:
        validate(instance=sc.data, schema=example_schema)
        # print("validated")
        return {"status": "valid"}
    except ValidationError as e:
        print("validation failed")
        return {"status": "invalid", "message": e.message}
