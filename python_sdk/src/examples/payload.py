import os
import sys
from datetime import date

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, root_dir)

# Determine if we're in development or production environment
is_development = os.path.basename(root_dir) == "python_sdk"

if is_development:
    from src.api.openapi_generated import (
        BinField,
        CalculatedField,
        DateRangeType,
        DifferenceTableCalcSpecification,
        DimensionField,
        DimensionFilterField,
        Direction,
        FilterType,
        Function,
        MatchFilter,
        MeasureField,
        MeasureFilterField,
        Parameter,
        PeriodType,
        QuantitativeDateFilter,
        QuantitativeFilterType,
        QuantitativeNumericalFilter,
        Query,
        RelativeDateFilter,
        SetFilter,
        TableCalcField,
        TableCalcFieldReference,
        TableCalcType,
        TopNFilter,
    )
else:
    from vizql_data_service_py.api.openapi_generated import (  # type: ignore
        CalculatedField,
        DateRangeType,
        DimensionField,
        DimensionFilterField,
        Direction,
        FilterType,
        Function,
        MatchFilter,
        MeasureField,
        MeasureFilterField,
        PeriodType,
        QuantitativeDateFilter,
        QuantitativeFilterType,
        QuantitativeNumericalFilter,
        Query,
        RelativeDateFilter,
        SetFilter,
        TopNFilter,
    )


def create_simple_query():
    return Query(
        fields=[
            DimensionField(fieldCaption="Category"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ]
    )


def create_custom_calculation():
    return Query(
        fields=[
            CalculatedField(
                fieldCaption="AOV", calculation="SUM([Profit])/COUNTD([Order ID])"
            ),
        ]
    )


def create_dimension_filter():
    return Query(
        fields=[
            DimensionField(fieldCaption="Ship Mode"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            SetFilter(
                field=DimensionFilterField(fieldCaption="Ship Mode"),
                filterType=FilterType.SET,
                values=["First Class", "Standard Class"],
                exclude=False,
            )
        ],
    )


def create_quantitative_range_filter():
    return Query(
        fields=[
            DimensionField(fieldCaption="Ship Mode"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            QuantitativeNumericalFilter(
                field=MeasureFilterField(fieldCaption="Sales", function=Function.SUM),
                filterType=FilterType.QUANTITATIVE_NUMERICAL,
                quantitativeFilterType=QuantitativeFilterType.RANGE,
                min=266839,
                max=1149562,
            )
        ],
    )


def create_quantitative_date_filter():
    return Query(
        fields=[
            MeasureField(fieldCaption="Order Date", function=Function.YEAR),
            MeasureField(fieldCaption="Order Date", function=Function.QUARTER),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            QuantitativeDateFilter(
                field=DimensionFilterField(fieldCaption="Order Date"),
                filterType=FilterType.QUANTITATIVE_DATE,
                quantitativeFilterType=QuantitativeFilterType.MIN,
                minDate=date(2020, 1, 1),
            )
        ],
    )


def create_relative_date_filter():
    return Query(
        fields=[
            MeasureField(
                fieldCaption="Order Date", function=Function.YEAR, sortPriority=1
            ),
            MeasureField(
                fieldCaption="Order Date", function=Function.MONTH, sortPriority=2
            ),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            RelativeDateFilter(
                field=DimensionFilterField(fieldCaption="Order Date"),
                filterType=FilterType.DATE,
                periodType=PeriodType.MONTHS,
                dateRangeType=DateRangeType.CURRENT,
                anchorDate=date(2022, 1, 1),
            )
        ],
    )


def create_match_filter():
    return Query(
        fields=[
            DimensionField(fieldCaption="State/Province"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            MatchFilter(
                field=DimensionFilterField(fieldCaption="State/Province"),
                filterType=FilterType.MATCH,
                startsWith="A",
                endsWith="a",
                contains="o",
                exclude=False,
            )
        ],
    )


def create_top_n_filter():
    return Query(
        fields=[
            DimensionField(fieldCaption="State/Province"),
            MeasureField(fieldCaption="Profit", function=Function.SUM),
        ],
        filters=[
            TopNFilter(
                field=DimensionFilterField(fieldCaption="State/Province"),
                filterType=FilterType.TOP,
                howMany=10,
                fieldToMeasure=MeasureFilterField(
                    fieldCaption="Profit", function=Function.SUM
                ),
                direction=Direction.TOP,
            )
        ],
    )


def create_multiple_dimension_filters():
    return Query(
        fields=[
            DimensionField(fieldCaption="Ship Mode"),
            DimensionField(fieldCaption="Segment"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            SetFilter(
                field=DimensionFilterField(fieldCaption="Ship Mode"),
                filterType=FilterType.SET,
                values=["First Class", "Standard Class"],
                exclude=False,
            ),
            SetFilter(
                field=DimensionFilterField(fieldCaption="Segment"),
                filterType=FilterType.SET,
                values=["Consumer"],
                exclude=True,
            ),
        ],
    )


def create_multiple_min_max_numeric_filters():
    return Query(
        fields=[
            DimensionField(fieldCaption="Ship Mode"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
            MeasureField(fieldCaption="Profit", function=Function.SUM),
        ],
        filters=[
            QuantitativeNumericalFilter(
                field=MeasureFilterField(fieldCaption="Sales", function=Function.SUM),
                filterType=FilterType.QUANTITATIVE_NUMERICAL,
                quantitativeFilterType=QuantitativeFilterType.MIN,
                min=266839,
            ),
            QuantitativeNumericalFilter(
                field=MeasureFilterField(fieldCaption="Profit", function=Function.SUM),
                filterType=FilterType.QUANTITATIVE_NUMERICAL,
                quantitativeFilterType=QuantitativeFilterType.MAX,
                max=164098,
            ),
        ],
    )


def create_dimension_numeric_filters():
    return Query(
        fields=[
            DimensionField(fieldCaption="Ship Mode"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            SetFilter(
                field=DimensionFilterField(fieldCaption="Ship Mode"),
                filterType=FilterType.SET,
                values=["First Class", "Standard Class"],
                exclude=True,
            ),
            QuantitativeNumericalFilter(
                field=MeasureFilterField(fieldCaption="Profit", function=Function.SUM),
                filterType=FilterType.QUANTITATIVE_NUMERICAL,
                quantitativeFilterType=QuantitativeFilterType.MIN,
                min=40000,
            ),
        ],
    )


def create_context_filter():
    return Query(
        fields=[
            DimensionField(fieldCaption="Sub-Category"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
        ],
        filters=[
            TopNFilter(
                field=DimensionFilterField(fieldCaption="Sub-Category"),
                filterType=FilterType.TOP,
                howMany=10,
                fieldToMeasure=MeasureFilterField(
                    fieldCaption="Sales", function=Function.SUM
                ),
                direction=Direction.TOP,
            ),
            SetFilter(
                field=DimensionFilterField(fieldCaption="Category"),
                filterType=FilterType.SET,
                values=["Furniture"],
                exclude=False,
                context=True,
            ),
        ],
    )


def create_numeric_date_dimension_filters():
    return Query(
        fields=[
            DimensionField(fieldCaption="Order Date"),
            MeasureField(fieldCaption="Sales", function=Function.SUM),
            DimensionField(fieldCaption="Ship Mode"),
        ],
        filters=[
            QuantitativeNumericalFilter(
                field=MeasureFilterField(fieldCaption="Sales", function=Function.SUM),
                filterType=FilterType.QUANTITATIVE_NUMERICAL,
                quantitativeFilterType=QuantitativeFilterType.RANGE,
                min=10,
                max=63,
            ),
            RelativeDateFilter(
                field=DimensionFilterField(fieldCaption="Order Date"),
                filterType=FilterType.DATE,
                periodType=PeriodType.MONTHS,
                dateRangeType=DateRangeType.NEXTN,
                rangeN=3,
                anchorDate=date(2022, 1, 1),
            ),
            SetFilter(
                field=DimensionFilterField(fieldCaption="Ship Mode"),
                filterType=FilterType.SET,
                values=["First Class"],
                exclude=False,
            ),
        ],
    )


def create_bin_formatting_with_parameter():
    return Query(
        fields=[
            DimensionField(fieldCaption="Profit (bin)", sortPriority=1),
        ],
        parameters=[Parameter(parameterCaption="Profit Bin Size", value=50)],
    )


def create_new_bin_field():
    return Query(
        fields=[
            MeasureField(fieldCaption="Sales", function=Function.SUM),
            BinField(fieldCaption="Profit", binSize=4000, sortPriority=1),
        ]
    )


def create_parameter_calculated_field():
    return Query(
        fields=[
            DimensionField(fieldCaption="Category"),
            DimensionField(fieldCaption="Country/Region"),
            CalculatedField(
                fieldCaption="Binned Profit",
                calculation="INT([Profit] / [Profit Bin Size]) * [Profit Bin Size]",
            ),
        ],
        parameters=[Parameter(parameterCaption="Profit Bin Size", value=200)],
    )


def create_simple_table_calculation():
    return Query(
        fields=[
            DimensionField(fieldCaption="Region", sortPriority=1),
            DimensionField(fieldCaption="Segment", sortPriority=2),
            TableCalcField(
                fieldCaption="Sales",
                function=Function.SUM,
                tableCalculation=DifferenceTableCalcSpecification(
                    tableCalcType=TableCalcType.DIFFERENCE_FROM,
                    dimensions=[
                        TableCalcFieldReference(fieldCaption="Region"),
                        TableCalcFieldReference(fieldCaption="Segment"),
                    ],
                    relativeTo="NEXT",
                ),
            ),
        ]
    )


QUERY_FUNCTIONS = [
    create_simple_query,
    create_custom_calculation,
    create_dimension_filter,
    create_quantitative_range_filter,
    create_quantitative_date_filter,
    create_relative_date_filter,
    create_match_filter,
    create_top_n_filter,
    create_multiple_dimension_filters,
    create_multiple_min_max_numeric_filters,
    create_dimension_numeric_filters,
    create_context_filter,
    create_numeric_date_dimension_filters,
    create_bin_formatting_with_parameter,
    create_new_bin_field,
    create_parameter_calculated_field,
    create_simple_table_calculation,
]
