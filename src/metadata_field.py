import re
from pydantic import BaseModel


class MetadataField(BaseModel):
    """
    メタデータのフィールドを表すクラス

    name: フィールド名 (プログラム中での変数やjsonのkeyとして用いられる名前)
    label: フォームに表示されるラベル
    qualifier: 登録フォーマットでの qualifier の種類 (e.g. ab_name, line, etc.)
    feature: 登録フォーマットでの feature の種類 (e.g. reference, keyword, etc.)
    entry: 登録フォーマットでの entry の種類 (どのようにして使うかまだ考えてない。廃止されるかも)
    type: データ型 array, string, boolean
    required: DDBJ登録に必須かどうかを表すフラグ
    pattern: 入力値バリデーションに用いる正規表現パターン
    default_value: デフォルト値
    private: 内部的に使うフィールドかどうかを表すフラグ (DFASTでは使っていたが、どのようにして使うか未定なので廃止されるかも)
    example: 入力例として表示される値
    help: ヘルプで表示されるメッセージ
    error_message: エラーメッセージ
    value: フィールドに入力された値を格納する
    """

    name: str
    label: str
    qualifier: str
    feature: str
    type: str
    required: str | bool
    pattern: str | re.Pattern
    default_value: str
    private: str | bool
    example: str
    help: str
    error_message: str
    value: str

    @staticmethod
    def read_definition(definition_file: str):
        """
        メタデータの定義ファイルを読み込み、MetadataFieldのリストを返す
        required, priveteについてはPythonのbool型に変換する

        Args:
            definition_file (str): tsv形式のメタデータ定義ファイルのパス

        Returns:
            list[Metadata]: MetadataFieldのリスト
        """
        L = []
        for line in open(definition_file):
            if line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            name, label, qualifier, feature, entry, type_, required, pattern, \
                default_value, private, example, help, error_message = cols
            required = True if required in ["YES", "TRUE"] else False
            # pattern = re.compile(r"^({0})$".format(pattern))

            field = MetadataField(
                name=name,
                label=label,
                qualifier=qualifier,
                feature=feature,
                entry=entry,
                type=type_,
                required=required,
                pattern=pattern,
                default_value=default_value,
                private=private,
                example=example,
                help=help,
                error_message=error_message,
                value=default_value
            )
            L.append(field)
        return L

    def set_value(self, value):
        self.value = value

    def get_values(self):
        """
        valueを取得。typeがarrayの場合にはリストに変換して返す
        """
        if self.type == "array":
            return [_.strip() for _ in self.value.split(";") if _.strip()]
        else:
            return self.value

    def to_mss(self):
        """
        MSS登録フォーマットの形式に変換
        """
        ret = []

        if (not self.required) and self.value == "":
            # 非必須フィールドで値が空の場合は出力しない
            return []
        if self.required and self.value == "":
            # 必須フィールドで値が空の場合はValueの値は空にして出力
            ret.append(["", "", "", self.qualifier, ""])
            if self.qualifier == "ab_name":
                # ab_name が空だった場合には、追加で２行をダミーの入力欄として挿入する
                ret.append(["", "", "", self.qualifier, ""])
                ret.append(["", "", "", self.qualifier, ""])
        elif self.type == "array":
            values = self.get_values()
            if self.feature == "ST_COMMENT" and values:  # ST_COMMENTの場合には複数行にしないで "; " で結合する
                ret.append(["", "", "", self.qualifier, "; ".join(values)])
            else:
                for value in values:
                    if value:
                        ret.append(["", "", "", self.qualifier, value])
        elif self.type == "boolean" and self.value:
            if self.value != "NO":
                ret.append(["", "", "", self.qualifier, ""])
        else:
            ret.append(["", "", "", self.qualifier, self.value])
        return ret

    def validate(self):
        """
        フィールドの値が正しいかどうかをチェック
        """
        if self.required and not self.value:
            return False  # 必須フィールドで値が空の場合はエラー
        re_pat = re.compile(r"^({0})$".format(self.pattern))
        if self.type == "array":
            if not all(re_pat.match(_) for _ in self.get_values()):
                self.error_message = f"Invalid value (acceptable pattern: '{self.pattern}')"
                return False
        elif self.type == "boolean":
            if self.value not in ["YES", "NO", "true", "false", "TRUE", "FALSE", "Trie", "False"]:
                self.error_message = f"Invalid value (acceptable pattern: '{self.pattern}')"
                return False
        else:  # string
            if not re_pat.match(self.value):
                self.error_message = f"Invalid value (acceptable pattern: '{self.pattern}')"
                return False
        return True


if __name__ == "__main__":
    """
    To run this script for debugging, use the following command:
    python -m src.metadata_field
    """


    definition_file = "metadata_definitions.tsv"
    metada_fields = MetadataField.read_definition(definition_file)
    # for field in MetadataField.read_definition(definition_file):
    #     print(field)

    # test for year field
    # year_field = [field for field in metada_fields if field.name == "year"][0]
    # print(year_field)
    # year_field.value = "2024"
    # print(year_field)  # True
    # print(year_field.validate())
    # year_field.value = "20240101"
    # print(year_field)  # False
    # print(year_field.validate())

    # test for keyword
    keyword_field = [field for field in metada_fields if field.name == "keyword"][0]
    print(keyword_field)
    keyword_field.value = "WGS"
    print(keyword_field)
    print(keyword_field.validate())  # True
    keyword_field.value = "WGS; STANDARD_DRAFT"
    print(keyword_field)
    print(keyword_field.validate())  # True
    keyword_field.value = "WGS; STANDARD_DRAFT, HOGE"
    print(keyword_field)
    print(keyword_field.validate())  # False    