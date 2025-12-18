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
        "QuantitativeFilterBase,": "QuantitativeNumericalFilter, QuantitativeDateFilter,",
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Add Literal filterType to each filter subclass for discriminator support
    filter_literals = [
        (
            "class MatchFilter(Filter):",
            "class MatchFilter(Filter):\n"
            "    filterType: Literal[FilterType.MATCH] = FilterType.MATCH",
        ),
        (
            "class ConditionFilter(Filter):",
            "class ConditionFilter(Filter):\n"
            "    filterType: Literal[FilterType.CONDITION] = FilterType.CONDITION",
        ),
        (
            "class QuantitativeNumericalFilter(QuantitativeFilterBase):",
            "class QuantitativeNumericalFilter(QuantitativeFilterBase):\n"
            "    filterType: Literal[FilterType.QUANTITATIVE_NUMERICAL] = "
            "FilterType.QUANTITATIVE_NUMERICAL",
        ),
        (
            "class QuantitativeDateFilter(QuantitativeFilterBase):",
            "class QuantitativeDateFilter(QuantitativeFilterBase):\n"
            "    filterType: Literal[FilterType.QUANTITATIVE_DATE] = "
            "FilterType.QUANTITATIVE_DATE",
        ),
        (
            "class SetFilter(Filter):",
            "class SetFilter(Filter):\n"
            "    filterType: Literal[FilterType.SET] = FilterType.SET",
        ),
        (
            "class RelativeDateFilter(Filter):",
            "class RelativeDateFilter(Filter):\n"
            "    filterType: Literal[FilterType.DATE] = FilterType.DATE",
        ),
        (
            "class TopNFilter(Filter):",
            "class TopNFilter(Filter):\n"
            "    filterType: Literal[FilterType.TOP] = FilterType.TOP",
        ),
    ]
    for old, new in filter_literals:
        content = content.replace(old, new)

    # Add TabFilter class with discriminator at the end of file
    tab_filter_code = """
class TabFilter(RootModel[Annotated[Union[
    MatchFilter, QuantitativeNumericalFilter, QuantitativeDateFilter, SetFilter, RelativeDateFilter, TopNFilter, ConditionFilter],
    PydanticField(discriminator='filterType')]]):
    root: Annotated[Union[
        MatchFilter, QuantitativeNumericalFilter, QuantitativeDateFilter, SetFilter, RelativeDateFilter, TopNFilter, ConditionFilter],
        PydanticField(discriminator='filterType')]
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
