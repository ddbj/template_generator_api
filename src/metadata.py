from pydantic import BaseModel, Field, EmailStr

class MetadataField(BaseModel):
    name: str = Field(...)
    label: str = Field(...)
    qualifier: str
    feature: str
    type: str
    required: str
    pattern: str
    default_value: str
    example: str
    help: str
    error_message: str
    value: str

    @staticmethod
    def read_definition(definition_file):
        L = []
        for line in open(definition_file):
            if line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            name, label, qualifier, feature, entry, type_, required, pattern, \
                default_value, private, example, help, error_message = cols
            field = MetadataField(
                name=name,
                label=label,
                qualifier=qualifier,
                feature=feature,
                type=type_,
                required=required,
                pattern=pattern,
                default_value=default_value,
                example=example,
                help=help,
                error_message=error_message,
                value=default_value
            )
            L.append(field)
        return L

if __name__ == "__main__":
    definition_file = "metadata_definitions.tsv"
    for field in MetadataField.read_definition(definition_file):
        print(field)

