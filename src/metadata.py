import os
import sys
import json
from copy import deepcopy
from pydantic import BaseModel, Field, EmailStr
from .metadata_field import MetadataField

METADATA_DEFINITION_FILE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/metadata_definitions.tsv"
METADATA_RULES_FILE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/metadata_rules.tsv"

BASE_METADATA_FIELDS = MetadataField.read_definition(definition_file=METADATA_DEFINITION_FILE)


class Metadata(BaseModel):
    """
    メタデータを格納するクラス
    """
    data_type: str = ""
    num_extra_references: int = 0
    num_extra_comments: int = 0
    fields: list[MetadataField] = Field(default_factory=list)
    options: str = ""

    @staticmethod
    def initialize(data_type: str="", num_extra_references: int=0, num_extra_comments: int=0, values: dict|None=None, options: str = ""):
        """
        data_typeと追加のReference, Commentの数に応じてメタデータフィールドを初期化する
        values (dict) が指定された場合には、その値をセットする。
        
        Args:
            data_type (str, optional): _description_. Defaults to "".
            num_extra_references (int, optional): _description_. Defaults to 0.
            num_extra_comments (int, optional): _description_. Defaults to 0.

        Returns:
            Metadata: _description_
        """
        metadata = Metadata(data_type=data_type, fields=deepcopy(BASE_METADATA_FIELDS))
        metadata.apply_rules(data_type)  # to be implemented
        for i in range(num_extra_references):
            metadata.add_extra_reference_fields()
        for i in range(num_extra_comments):
            metadata.add_extra_comment_field()
        if values:
            metadata.set_values(values)
        return metadata

    @staticmethod
    def initialize_from_values(values: dict, data_type=""):
        """
        メタデータの値に応じてメタデータフィールドを初期化し、値をセットする
        (既存ツールとの互換性のために実装したが使わないかも)

        Args:
            values (dict): _description_
            data_type (str, optional): _description_. Defaults to "".
        """
        def _get_extra(field_type: str):
            # extra references or commentsの数を取得する
            # field_type: "reference" or "comment"
            extra_fields = [int(k.replace(field_type + "__", "")) for k in values.keys() if field_type + "__" in k]
            if extra_fields:
                return max(extra_fields) - 1
            else:
                return 0  # extra field がない場合は0を返す 
              
        num_extra_references = _get_extra("reference")
        num_extra_comments = _get_extra("comment")
        metadata = Metadata.initialize(data_type=data_type, num_extra_references=num_extra_references, 
                                       num_extra_comments=num_extra_comments, values=values)
        return metadata

    def apply_rules(self, data_type: str):
        # TODO: メタデータのルールを適用する
        sys.stderr.write("Applying metadata rules... (To be implemented)\n")
        

    def set_example_values(self):
        """
        メタデータのフィールドに入力例をセットする. テスト、動作確認用
        """
        for field in self.fields:
            field.value = field.example

    def set_values(self, values: dict):
        """
        メタデータのフィールドに値をセットする

        Args: values (dict): フィールド名をキー、値をバリューとする辞書
        """
        for field in self.fields:
            if field.name in values:
                field.value = values[field.name]

    def validate_values(self):
        """
        (仮実装) メタデータの値をバリデーションする。どのような形式で返すかは未定

        Returns:
            _type_: _description_
        """
        for field in self.fields:
            field.validate()


    def to_mss(self, format: str = "array"):
        """
        メタデータをMSS登録ファイル形式で返す

        デフォルトでは５列の表形式アレイ [[str, str, str, str, str], [str, str, str, str, str], ...] の形で返す
        format="text" を指定するとタブ区切りのテキスト形式で返す
        """
        # featureの種類を取得
        # e.g. ['DIVISION', 'DATATYPE', 'KEYWORD', 'DBLINK', 'SUBMITTER', 'REFERENCE', 'OTHER', 'DATE', 'COMMENT', 'COMMENT:EST', 'ST_COMMENT', 'source']
        features = [field.feature for field in self.fields]
        feature_types = sorted(set(features), key=features.index)

        ret = []
        for feature_type in feature_types:
            # feature_typeごとにMSS形式に変換し feature_block に格納
            feature_block = []
            fields = [field for field in self.fields if field.feature == feature_type]
            for field in fields:
                feature_block += field.to_mss()
            if feature_block:
                # feature_block が空でなければ2列目に feature 名を記載して ret に追加
                # comment, reference に追加のブロックがある場合にはfeature名に __2, __3 などが追加されるので削除する必要がある。
                feature_block[0][1] = feature_type.split("__")[0]
                ret += feature_block

        if format == "text":
            ret = "\n".join(["\t".join(row) for row in ret])

        return ret

    def add_extra_comment_field(self):
        """
        Comment フィールドを追加する
        """
        self.num_extra_comments += 1
        base_field = [field for field in self.fields if field.name == "comment"][0]
        extra_field: MetadataField = deepcopy(base_field)
        extra_field.name = f"comment__{self.num_extra_comments + 1}"
        extra_field.feature = f"COMMENT__{self.num_extra_comments + 1}"
        extra_field.value = ""
        self.fields.append(extra_field)

    def remove_extra_comment_field(self):
        """
        追加の Comment フィールドのうち、 comment__# の # が最大のものを削除する
        """
        if self.num_extra_comments > 0:
            self.fields = [field for field in self.fields if field.name != "comment__" + str(self.num_extra_comments + 1)]
            self.num_extra_comments -= 1


    def add_extra_reference_fields(self):
        """
        Reference フィールドを追加する

        To be discussed: set_default_values をつけるか検討
        """
        self.num_extra_references += 1
        target_fields = ["reference", "author", "ref_consrtm", "status", "year", "journal", "volume", "start_page", "end_page", "pubmed"]

        for target_field in target_fields:
            base_field = [
                field for field in self.fields if field.name == target_field][0]
            extra_field: MetadataField = deepcopy(base_field)
            extra_field.name = f"{extra_field.name}__{self.num_extra_references + 1}"
            extra_field.feature = f"{extra_field.feature}__{self.num_extra_references + 1}"
            extra_field.value = extra_field.default_value
            self.fields.append(extra_field)

    def remove_extra_reference_fields(self):
        """
        追加の Reference フィールドのうち、 FIELD_NAME__# の # が最大のものを削除する
        """
        if self.num_extra_references > 0:
            target_fields = ["reference", "author", "ref_consrtm", "status", "year", "journal", "volume", "start_page", "end_page", "pubmed"]
            target_fields = [f"{field}__{self.num_extra_references + 1}" for field in target_fields]
            self.fields = [field for field in self.fields if field.name not in target_fields]
            self.num_extra_references -= 1

    def to_json(self):
        """
        debug用。メタデータのフィールド名と値をjson形式で返す

        Returns:
            _type_: _description_
        """
        D = {field.name: field.value for field in self.fields}
        return json.dumps(D, indent=4)


if __name__ == "__main__":
    """
    To run this script for debugging, use the following command:
    python -m src.metadata
    """


    # metadata = Metadata()
    # metadata = Metadata.initialize(num_extra_comments=2, num_extra_references=1)
    # print(metadata)
    # metadata.set_example_values()
    # # print(metadata.to_json())
    # metadata.add_extra_comment_field()
    # metadata.add_extra_comment_field()
    # metadata.add_extra_reference_fields(set_default_values=True)
    values = {  "division": "",
      "keyword": "WGS; whole-genome shotgun sequencing",
      "comment__3": "This is a test comment 3; test comment 3 line2",
      "comment__2": "This is a test comment 2; test comment 2 line2",
      "reference__2": "Mouse Genome Sequencing 2",
      }
    metadata = Metadata.initialize_from_values(values=values, data_type="WGS")
    metadata.set_example_values()
    metadata.set_values(values)
    # print(metadata.num_extra_references)
    metadata.remove_extra_reference_fields()
    # print(metadata.num_extra_references)
    # metadata.remove_extra_comment_field()

    # print(metadata.to_json())
    print(metadata.model_dump_json())
    # print(metadata.fields)
    # metadata.set_values(values)
    # print(metadata.to_mss(format="text"))
