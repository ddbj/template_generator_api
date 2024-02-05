from pydantic import BaseModel, Field
from .metadata import Metadata
from .metadata_field import MetadataField
from .metadata_values import MetadataValues

template_example = [["COMMON", "SUBMITTER", "", "ab_name", "Robertson,G.R."], ["COMMON", "", "", "ab_name", "Mishima,H."], ["", "DBLINK", "", "project", "PRJDB12345"]]
values_example = {"submitter": "Robertson,G.R.; Mishima,H.", "bioproject": "PRJDB12345"}

class MetadataRequest(BaseModel):
    """
    メタデータ定義およびMSS登録フォーマットのテンプレートを返すためのリクエストスキーマ  
    全てのフィールドはoptional  
    optionsについてはどのように使うかは未定。将来辞書型に変更する可能性がある。
    """
    data_type: str = ""
    num_extra_references: int = 0
    num_extra_comments: int = 0
    values: MetadataValues|None = Field(default_factory=list, title="template", description="key-value pair of metadata", examples=[values_example])
    options: str = ""

class MetadataResponse(BaseModel):
    """
    メタデータ定義およびMSS登録フォーマットのテンプレートを含むレスポンススキーマ
    """

    metadata: Metadata
    template: list[list[str]] = Field(default_factory=list, title="template", description="MSS template in 5-column table", examples=[template_example])

if __name__ == "__main__":

    res = MetadataResponse()
    print(res)