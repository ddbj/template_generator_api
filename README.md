# dtg_api
DDBJ Template Generator API

## 起動
port:8000
```
docker-compose up
```

API Docs: http://localhost:8000/docs

# JSON schema 開発版

## テスト用 schema  

[`src/dev_schemas`](src/dev_schemas) 以下に配置。

| 名前 | ファイル名 | 説明 |
| ---- | ---- | ---- |
| minimum | [example_schema_minimum.json](src/dev_schemas/example_schema_minimum.json) | テスト用最小構成 | 
| submission_category | [submission_category.json](src/dev_schemas/submission_category.json)  | 登録カテゴリごとに条件分岐 |
| reference | [reference_schema.json](src/dev_schemas/reference_schema.json)  | 参考文献用 |
| multi_reference | [reference_schema_multi.json](src/dev_schemas/reference_schema_multi.json)  | 参考文献の複数指定を許容 |
| ddbj_dev1 | [ddbj_submission_dev1.json](src/dev_schemas/ddbj_submission_dev1.json)  | 全部入り |

## schema 取得
```
curl -X 'POST' \
  'http://localhost:8000/dev/schema' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "minimum"
}'
```
`name`の部分は `minimum`, `submission_category`, `reference`, `multi_reference`, `ddbj_dev1` から指定。

## validation
Python の jsonschema ライブラリを使用。
```
curl -X 'POST' \
  'http://localhost:8000/dev/validate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "minimum",
  "data": { "keyword": [ "WGS", "STANDARD_DRAFT" ], "biosample": [], "data_type": "WGS", "contact": "John" }
}'
```

## memo
React Json Schema Form でフォームが生成できることを確認。  
`definitions` を使用してサブスキーマに分割した場合、フォームが生成されるもののdefault値が反映されない問題あり (`submission_category` では動いたが、`dev1` にすると期待通りに動かない。validation はできたので正しい形式にはなっていると思われる。)  
[svelte 用のライブラリ](https://github.com/webgme/svelte-jsonschema-form) に対応していない可能性あり。[Svelte JSON Schema Form Playground](https://github.com/webgme/svelte-jsonschema-form#:~:text=Svelte%20JSON%20Schema%20Form%20Playground) で試すと一部動作しなかった。


---
# 以下は、独自仕様のAPI版の情報

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



## 開発用 client app
docker-compose-dev.yml で起動すると React JSONschema を使ってフォームの自動生成ができる。  
http://localhost:3000

```
# module install
docker-compose -f docker-compose-dev.yml run --rm client npm install 

# 起動
docker-compose -f docker-compose-dev.yml up
```