from fastapi import FastAPI
from .metadata import Metadata
from .schemas import MetadataRequest, MetadataResponse

from .dev_router import router as dev_router
app = FastAPI()
app.include_router(dev_router)

VERSION = "0.2.0"


@app.get("/")
async def get_version():
    return {"DDBJ_Template_Generator": VERSION}


@app.post("/update/", response_model=MetadataResponse)
@app.post("/create/", response_model=MetadataResponse)
async def get_metadata_definition_and_template(metadata_request: MetadataRequest):
    """
    data_type, num_extra_references, num_extra_comments に応じてメタデータ定義と、MSS登録フォーマットのテンプレートを返す。  
    create は最初に定義を取得するときに使用することを想定。この場合には values は空でよい。  
    uppdate は既存の定義を取得するときに使用することを想定。この場合には values に既存の値を送信する。  
    create および update は現状同じ処理を行なっているが、エンドポイントは別にしている。
    
    Args: metadata_request (MetadataRequest)  
        例:
        ```
            {
                "data_type": "",
                "num_extra_references": 0,
                "num_extra_comments": 0,
                "values": {"ab_name": "Mishima,H.", "project": "PRJDB12345", ...},
                "options": ""
            }
        ```
    Returns: MetadataResponse
    """
    metadata = Metadata.initialize(**metadata_request.model_dump())
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())


@app.post("/add_comment/", response_model=MetadataResponse)
async def add_comment(metadata_request: MetadataRequest):
    """
    commentフィールドを追加し、メタデータ定義と、MSS登録フォーマットのテンプレートを返す。  
    送信するjsonはcreate/updateと同じ。  
    num_extra_comments は現在の設定値を送信すること。+1された値が返される。  
        例:
        ```
            {
                "data_type": "",
                "num_extra_references": 0,
                "num_extra_comments": 0,
                "values": {"ab_name": "Mishima,H.", "project": "PRJDB12345", ...},
                "options": ""
            }
        ```
    """
    metadata = Metadata.initialize(**metadata_request.model_dump())
    metadata.add_extra_comment_field()
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())

@app.post("/remove_comment/", response_model=MetadataResponse)
async def remove_comment(metadata_request: MetadataRequest):
    """
    commentフィールドを1つ削除し、メタデータ定義と、MSS登録フォーマットのテンプレートを返す。  
    送信するjsonはcreate/updateと同じ。  
    num_extra_comments は現在の設定値を送信すること。-1された値が返される。  
    """
    metadata = Metadata.initialize(**metadata_request.model_dump())
    metadata.remove_extra_comment_field()
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())

@app.post("/add_reference/", response_model=MetadataResponse)
async def add_reference(metadata_request: MetadataRequest):
    """
    referenceフィールドを追加し、メタデータ定義と、MSS登録フォーマットのテンプレートを返す。  
    送信するjsonはcreate/updateと同じ。  
    num_extra_references は現在の設定値を送信すること。+1された値が返される。
    """
    metadata = Metadata.initialize(**MetadataRequest.model_dump())
    metadata.add_extra_reference_fields()
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())

@app.post("/remove_reference/", response_model=MetadataResponse)
async def remove_reference(metadata_request: MetadataRequest):
    """
    referenceフィールドを1つ削除し、メタデータ定義と、MSS登録フォーマットのテンプレートを返す。
    送信するjsonはcreate/updateと同じ。  
    num_extra_references は現在の設定値を送信すること。-1された値が返される。
    """
    metadata = Metadata.initialize(**metadata_request.model_dump())
    metadata.remove_extra_reference_fields()
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())


@app.post("/validate/", response_model=MetadataResponse)
async def validate_metadata(metadata_request: MetadataRequest):
    """
    (未実装) メタデータの値をバリデーションし、エラーがあれば定義情報にエラーメッセージを追加して返す  
    送信するjsonはcreate/updateと同じ。  
    """
    metadata = Metadata.initialize(**metadata_request.model_dump())
    metadata.validate_values()
    return MetadataResponse(metadata=metadata, template=metadata.to_mss())





##### DEBUG #####
# @app.get("/test/")
# async def test():
#     metadata = Metadata.initialize()
#     return {metadata.to_json()}


# class Item(BaseModel, extra="allow"):
#     name: str = Field("", title="The name of the item", description="The name of the item", examples=["DEFAULT NAME", "DEF2"])
#     description: str = None
#     price: float
#     tax: float = None

#     # class Config:
#     #     extra = Extra.allow

# @app.post("/items/")
# async def create_item(item: Item):
#     """_summary_

#     Args:
#         item (Item): _description_

#     Returns:
#         _type_: _description_
#     """
#     print(item)
#     item.price = item.price * (1 + item.tax) # + item.price_2
#     print(item.model_dump())
#     additional_param = item.model_dump().get("comment/2", "default value")
#     print(additional_param)
#     return {"name": item.name, "price": item.price}