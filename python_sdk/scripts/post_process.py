import os
import re


def convert_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex replacements
    replacementsRegex = {
        r"\bField\(": r"PydanticField(",
        r"    model_config = ConfigDict\(\n        extra=\'forbid\',\n    \)\n": "",
    }

    for old, new in replacementsRegex.items():
        content = re.sub(old, new, content)

    # Non-regex replacements
    replacements = {
        "FieldModel": "Field",
        "Optional[List[Filter]]": "Optional[List[TabFilter]]",
        ", Field, ": ", Field as PydanticField, ",
        " ConfigDict,": "",
        "import TableauModel": "from .tableau_model import TableauModel",
        "ParameterRecord": "ParameterRecordBase",
        "Optional[List[ParameterRecordBase]]": "Optional[List[ParameterRecord]]",
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Add TabFilter class at the end of file
    tab_filter_code = """
class TabFilter(RootModel[Union[
    MatchFilter, QuantitativeNumericalFilter, QuantitativeDateFilter, SetFilter, RelativeDateFilter, TopNFilter]]):
    root: Union[
        MatchFilter, QuantitativeNumericalFilter, QuantitativeDateFilter, SetFilter, RelativeDateFilter, TopNFilter]
"""
    content += tab_filter_code

    # Add ParameterRecord class at the end of file
    parameter_record = """
class ParameterRecord(RootModel[Union[
    AnyValueParameter, ListParameter, QuantitativeRangeParameter, QuantitativeDateParameter]]):
    root: Union[
        AnyValueParameter, ListParameter, QuantitativeRangeParameter, QuantitativeDateParameter]
"""
    content += parameter_record

    # Write to output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    convert_file("src/api/openapi_generated-raw.py", "src/api/openapi_generated.py")
    os.remove("src/api/openapi_generated-raw.py")
