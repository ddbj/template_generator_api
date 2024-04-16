// import { RJSFSchema } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
// import Form from '@rjsf/core';
import Form from '@rjsf/bootstrap-4';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import 'bootstrap/dist/css/bootstrap.min.css';

// for debugging
// const schema: RJSFSchema = {
//   title: 'Todo',
//   type: 'object',
//   required: ['title'],
//   properties: {
//     title: { type: 'string', title: 'Title', default: 'A new task' },
//     done: { type: 'boolean', title: 'Done?', default: false },
//   },
// };

// submit ボタンを非表示にする
const uiSchema = {
    // この部分でsubmitボタンをカスタマイズ
    "ui:submitButtonOptions": {
      "noreferrer": true, // カスタムプロパティを追加することも可能
      "props": {
        "style": {
          "display": "none" // submitボタンを非表示にする
        }
      }
    }
  };



const log = (type) => console.log.bind(console, type);

function App() {

    const [schemaName, setSchemaName] = useState("reference");
    const [schemaTypes, setSchemaTypes] = useState(null);
    const [schema, setSchema] = useState(null);
    const [formData, setFormData] = useState(null);

    useEffect(() => {
        // schemaの一覧を取得
        console.log("fetching schema types")
        axios.get('http://localhost:8000/dev/get_schema_types', {
            params: { _: new Date().getTime() }
        })
            .then(response => setSchemaTypes(response.data)) // レスポンスからデータを取得してセット
            .catch(error => console.error('Error fetching data:', error));
    }, []); // 空の依存配列でエフェクトを一度だけ実行


    useEffect(() => {
        // jsonschema 取得
        console.log("Schema Selected:", schemaName)
        fetch_schema(schemaName);
    }, [schemaName]);


    const fetch_schema = (name) => {
        // jsonschema 取得
        axios.post('http://localhost:8000/dev/schema', { name: name })
            .then((response) => { console.log("fetched"); setSchema(response.data) }) // レスポンスからデータを取得してセット
            .catch(error => console.error('Error fetching data:', error));
    }

    const on_schema_type_change = (e) => {
        console.log(e.formData.name);
        setSchemaName(e.formData.name);
    }

    const on_form_change = (e) => {
        console.log(e.formData);
        setFormData(e.formData);
    }

    const validate = () => {
        axios.post('http://localhost:8000/validate', { name: schemaName, data: formData })
            .then((response) => { console.log(response.data) }) // レスポンスからデータを取得してセット
            .catch(error => console.error('Error fetching data:', error));
    }

    return (
        <div className="App container">
            <Row>
                <Col>
                    {schemaTypes ?
                        <Form schema={schemaTypes} validator={validator} uiSchema={uiSchema} onChange={on_schema_type_change}>
                        </Form>
                        :
                        <p>loading...</p>
                    }
                    <button onClick={() => fetch_schema(schemaName)}>Fetch Schema</button>
                    <hr /><br /><br />

                    {schema ?
                        <Form
                            schema={schema}
                            validator={validator}
                            onChange={on_form_change}
                            onSubmit={log('submitted')}
                            onError={log('errors')}
                        >

                        </Form>

                        :
                        <p>loading...</p>
                    }
                            <button onClick={() => validate()}>Validation</button>

                </Col>
                <Col>
                    <h3>Form Data</h3>
                    {formData ? <code>{JSON.stringify(formData, null, 2)}</code> : <p>...</p>}
                    <h3>Schema</h3>
                    {schema ? <code>{JSON.stringify(schema, null, 2)}</code> : <p>...</p>}
                </Col>
            </Row>
        </div>
    );
}

export default App;
