# dtg_api
DDBJ Template Generator API

## 起動
port:8000
```
docker-compose up
```

API Docs: http://localhost:8000/docs

## 基本機能
### メタデータ入力欄の定義情報およびMSS登録ファイルのテンプレートを返す
#### リクエストについて
- data_type, num_extra_references, num_extra_comments および各メタデータの値を送信し、メタデータ入力フォームの定義とMSS登録フォーマットのテンプレートを返す。  
- 基本機能に関するメソッドでは共通して以下の形式の json (`MetadataRequest`モデルとして定義されている) を送信する
```
    {
        "data_type": "",
        "num_extra_references": 0,
        "num_extra_comments": 0,
        "values": {"submitter": "Robertson,G.R.; Mishima,H.", "bioproject": "PRJDB12345", ...},
        "options": ""
    }
```
- `data_type`: 登録するデータの区分を示す。データ区分に応じてメタデータの定義情報が変わる (例: WGSの登録カテゴリではBioProjectとBioSampleの登録が必須になる、など)。
- `num_extra_references` と `num_extra_comments`: 追加のREFERENCEとCOMMENTを記載するときに使う (後述)
- `options`: 未実装。将来、辞書またはリストに変更する可能性あり。
- `values` について  
    最初に定義を指定するときには空 `{}` で良い。既存のデータがある場合 (ビューを更新する場合) には既存の値を送信する。key には `MetadataValues` (`metadata_values.py`) に定義されている変数名を使用する。送信した値はメタデータ定義の `value` に格納されて返される。
#### レスポンスについて
- レスポンスの形式 (`MetadataResponse` モデル) は以下の通り
```
{
  "metadata": {
    "data_type": "",
    "num_extra_references": 0,
    "num_extra_comments": 0,
    "fields": [
      {
        "name": "string", "label": "string",
        "qualifier": "string",
        "feature": "string",
        "type": "string",
        "required": "string",
        "pattern": "string",
        "default_value": "string",
        "private": "string",
        "example": "string",
        "help": "string",
        "error_message": "string",
        "value": "string"
      }, ...
    ]
  },
  "template": [
    ["COMMON", "SUBMITTER", "", "ab_name", "Robertson,G.R."],
    ["COMMON", "", "", "ab_name", "Mishima,H."],
    ["", "DBLINK", "", "project", "PRJDB12345"],
    ...
  ]
}
```
- `metadata` の `fields` は `MetadataField` で定義されたオブジェクトのリストになっている。
- `MetadataField` の `type` は string (単独の値), array (複数の値), boolean の 3 種類。ただし array の場合は `; ` で連結された文字列としてjsonの送受信を行なっている。
- `pattern` はバリデーションに用いる Regex のパターン文字列
- `type` と `pattern` の組み合わせで、入力フォームの種類が決まる (自由テキスト入力 or 選択式、複数入力を許容するかなど)
- レスポンスの `template` は 5列の表形式データ (二次元配列)

### 追加の REFERENCE および COMMENT の入力について
- それぞれについて追加・削除を行うメソッドを用意
- 送信時の json の形式は上述のものと同じ。`num_extra_references` と `num_extra_comments` については現在の設定値を送信する。レスポンスでは +1 あるいは -1 されたものが返される。
- COMMENT を追加した場合 `comment__2`、`comment__3`、 ... という名前の `MetadataField` が追加される。送信時の json の key でも追加されたものを用いる。(以前のAPIでは `comment:2` という形式だったがプログラム内で扱いについので `__` に変更)
- 同様に REFERENCE を追加した場合には `reference__2`、`reference__3`、 ...、`author__2`、`author__3`、... などが追加される。

### Validation について
- 実装方法は検討中
- (仮実装) バリデーションに失敗した場合には `MetadataField` の `error_message` にエラーメッセージを格納してメタデータ定義を返す。
- 今のところ送受信の json の形式は上述のものと同じ。
- バリデーションには単独の値の入力規則チェックだけではなく、複数の入力フィールドにまたがるチェックも含まれる予定 (共起、排他チェックなど)
- `strict` オプションを実装予定。デフォルトでは `False` に設定し、必須項目が入力されていなくても許容とする。有効にした場合には必須項目に値が入力されていない場合にはエラーとする。

