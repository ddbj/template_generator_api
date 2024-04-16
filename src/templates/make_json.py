from jinja2 import Template, Environment, FileSystemLoader
import json

json_template_file = 'template_dev2.json'
test_out_file = json_template_file + ".test.json"
out_json_file = 'ddbj_submission_dev2.json'

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template_dev2.json')


# template = Template('''\
# test''')

json_str = template.render()
# print(json_str) 
with open(test_out_file , 'w') as f:
    f.write(json_str)
json_dat = json.loads(json_str)
# print(json_dat)

json_dat = json.loads(json_str)
json.dump(json_dat, open(out_json_file, 'w'), indent=4)
