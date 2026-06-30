import argparse
import datetime

import pytest

from src.api.openapi_generated import (
    Datasource,
    DataType,
    DateRangeType,
    DimensionField,
    DimensionFilterField,
    FilterType,
    Function,
    MeasureField,
    MetadataOutput,
    MovingTableCalcSpecification,
    ParameterType,
    PeriodType,
    QuantitativeFilterType,
    QuantitativeRangeParameter,
    Query,
    QueryDatasourceOptions,
    QueryRequest,
    ReadMetadataRequest,
    RelativeDateFilter,
    RunningTotalTableCalcSpecification,
    TableCalcComputedAggregation,
    TableCalcFieldReference,
    TableCalcType,
)
from src.examples import common
from src.examples.payload import (
    WORKBOOK_QUERY_FUNCTIONS,
    create_simple_workbook_query,
    create_workbook_bin_formatting_with_parameter,
    create_workbook_custom_calculation,
    create_workbook_new_bin_field,
)


def _unwrap(obj):
    return obj.root if hasattr(obj, "root") else obj


@pytest.fixture
def sample_metadata_request():
    return {"datasource": {"datasourceLuid": "74ff134d-7f8f-475c-a63e-bf14ea26cbb1"}}


@pytest.fixture
def sample_metadata_output():
    return {
        "data": [
            {
                "fieldName": "Returned",
                "fieldCaption": "Returned",
                "dataType": "STRING",
                "defaultAggregation": "COUNT",
                "logicalTableId": "Returns_2AA0FE4D737A4F63970131D0E7480A03",
                "columnClass": "COLUMN",
            },
            {
                "fieldName": "Category",
                "fieldCaption": "Category",
                "dataType": "STRING",
                "defaultAggregation": "COUNT",
                "logicalTableId": "Orders_ECFCA1FB690A41FE803BC071773BA862",
                "columnClass": "COLUMN",
            },
        ],
        "extraData": {
            "parameters": [
                {
                    "parameterType": "QUANTITATIVE_RANGE",
                    "parameterName": "Parameter 1",
                    "parameterCaption": "Top Customers",
                    "dataType": "INTEGER",
                    "value": 5.0,
                    "min": 5.0,
                    "max": 20.0,
                    "step": 5.0,
                },
            ]
        },
    }


@pytest.fixture
def sample_query_request():
    return {
        "datasource": {"datasourceLuid": "74ff134d-7f8f-475c-a63e-bf14ea26cbb1"},
        "query": {
            "fields": [
                {"fieldCaption": "Order Date"},
                {"fieldCaption": "Sales", "function": Function.SUM},
                {"fieldCaption": "Ship Mode"},
            ],
            "filters": [
                {
                    "field": {"fieldCaption": "Sales", "function": Function.SUM},
                    "filterType": FilterType.QUANTITATIVE_NUMERICAL,
                    "quantitativeFilterType": QuantitativeFilterType.RANGE,
                    "min": 10,
                    "max": 63,
                },
                {
                    "filterType": FilterType.DATE,
                    "field": {"fieldCaption": "Order Date"},
                    "periodType": PeriodType.MONTHS,
                    "dateRangeType": DateRangeType.NEXTN,
                    "rangeN": 3,
                    "anchorDate": "2021-01-01",
                },
                {
                    "field": {"fieldCaption": "Ship Mode"},
                    "filterType": FilterType.SET,
                    "values": ["First Class"],
                    "exclude": False,
                },
            ],
        },
    }


def test_read_metadata_request_from_obj(sample_metadata_request):
    """Test creating ReadMetadataRequest instance from dictionary"""
    request = ReadMetadataRequest.model_validate(sample_metadata_request)
    assert request.datasource.datasourceLuid == "74ff134d-7f8f-475c-a63e-bf14ea26cbb1"
    assert request.datasource.connections is None


def test_metadata_output_from_obj(sample_metadata_output):
    """Test creating MetadataOutput instance from dictionary"""
    output = MetadataOutput.model_validate(sample_metadata_output)

    # Test data field
    assert output.data is not None
    assert len(output.data) == 2

    # Test first field (Returned)
    returned_field = output.data[0]
    assert returned_field.fieldName == "Returned"
    assert returned_field.fieldCaption == "Returned"
    assert returned_field.dataType == DataType.STRING
    assert returned_field.logicalTableId == "Returns_2AA0FE4D737A4F63970131D0E7480A03"

    # Test second field (Category)
    category_field = output.data[1]
    assert category_field.fieldName == "Category"
    assert category_field.fieldCaption == "Category"
    assert category_field.dataType == DataType.STRING
    assert category_field.logicalTableId == "Orders_ECFCA1FB690A41FE803BC071773BA862"

    # Test extraData parameters
    assert output.extraData is not None
    assert output.extraData.parameters is not None
    assert len(output.extraData.parameters) == 1

    param = _unwrap(output.extraData.parameters[0])
    assert isinstance(param, QuantitativeRangeParameter)
    assert param.parameterType == ParameterType.QUANTITATIVE_RANGE
    assert param.parameterName == "Parameter 1"
    assert param.parameterCaption == "Top Customers"
    assert param.dataType == DataType.INTEGER
    assert param.value == 5.0
    assert param.min == 5.0
    assert param.max == 20.0
    assert param.step == 5.0


def test_metadata_output_to_dict(sample_metadata_output):
    """Test converting MetadataOutput instance to dictionary"""
    output = MetadataOutput.model_validate(sample_metadata_output)
    output_dict = output.model_dump()

    assert isinstance(output_dict, dict)
    assert "data" in output_dict
    assert len(output_dict["data"]) == 2

    # Test first field (Returned)
    returned_field = output_dict["data"][0]
    assert returned_field["fieldName"] == "Returned"
    assert returned_field["fieldCaption"] == "Returned"
    assert returned_field["dataType"] == DataType.STRING
    assert (
        returned_field["logicalTableId"] == "Returns_2AA0FE4D737A4F63970131D0E7480A03"
    )

    # Test second field (Category)
    category_field = output_dict["data"][1]
    assert category_field["fieldName"] == "Category"
    assert category_field["fieldCaption"] == "Category"
    assert category_field["dataType"] == DataType.STRING
    assert category_field["logicalTableId"] == "Orders_ECFCA1FB690A41FE803BC071773BA862"

    # Test extraData parameters
    assert "extraData" in output_dict
    assert output_dict["extraData"]["parameters"] is not None
    assert len(output_dict["extraData"]["parameters"]) == 1

    param = output_dict["extraData"]["parameters"][0]
    assert param["parameterType"] == ParameterType.QUANTITATIVE_RANGE
    assert param["parameterName"] == "Parameter 1"
    assert param["parameterCaption"] == "Top Customers"
    assert param["dataType"] == DataType.INTEGER
    assert param["value"] == 5.0
    assert param["min"] == 5.0
    assert param["max"] == 20.0
    assert param["step"] == 5.0


def test_query_request_from_dict(sample_query_request):
    """Test creating QueryRequest instance from dictionary"""
    request = QueryRequest.model_validate(sample_query_request)

    # Test datasource
    assert request.datasource.datasourceLuid == "74ff134d-7f8f-475c-a63e-bf14ea26cbb1"

    # Test fields
    assert len(request.query.fields) == 3
    field0 = _unwrap(request.query.fields[0])
    assert isinstance(field0, DimensionField)
    assert field0.fieldCaption == "Order Date"
    field1 = _unwrap(request.query.fields[1])
    assert isinstance(field1, MeasureField)
    assert field1.fieldCaption == "Sales"
    assert field1.function == Function.SUM
    field2 = _unwrap(request.query.fields[2])
    assert isinstance(field2, DimensionField)
    assert field2.fieldCaption == "Ship Mode"

    # Test filters
    assert len(request.query.filters) == 3

    # Test quantitative filter
    quant_filter = _unwrap(request.query.filters[0])
    assert quant_filter.filterType == FilterType.QUANTITATIVE_NUMERICAL
    assert quant_filter.quantitativeFilterType == QuantitativeFilterType.RANGE
    assert quant_filter.min == 10
    assert quant_filter.max == 63
    assert _unwrap(quant_filter.field).fieldCaption == "Sales"
    assert _unwrap(quant_filter.field).function == Function.SUM

    # Test date filter
    date_filter = _unwrap(request.query.filters[1])
    assert date_filter.filterType == FilterType.DATE
    assert date_filter.periodType == PeriodType.MONTHS
    assert date_filter.dateRangeType == DateRangeType.NEXTN
    assert date_filter.rangeN == 3
    assert date_filter.anchorDate == datetime.date(2021, 1, 1)
    assert _unwrap(date_filter.field).fieldCaption == "Order Date"

    # Test set filter
    set_filter = _unwrap(request.query.filters[2])
    assert set_filter.filterType == FilterType.SET
    assert [_unwrap(value) for value in set_filter.values] == ["First Class"]
    assert set_filter.exclude is False
    assert _unwrap(set_filter.field).fieldCaption == "Ship Mode"


def test_query_request_to_dict(sample_query_request):
    """Test converting QueryRequest instance to dictionary"""
    request = QueryRequest.model_validate(sample_query_request)
    request_dict = request.model_dump()

    assert isinstance(request_dict, dict)
    assert (
        request_dict["datasource"]["datasourceLuid"]
        == "74ff134d-7f8f-475c-a63e-bf14ea26cbb1"
    )

    # Test fields
    assert len(request_dict["query"]["fields"]) == 3
    assert request_dict["query"]["fields"][0]["fieldCaption"] == "Order Date"
    assert request_dict["query"]["fields"][1]["fieldCaption"] == "Sales"
    assert request_dict["query"]["fields"][1]["function"] == Function.SUM
    assert request_dict["query"]["fields"][2]["fieldCaption"] == "Ship Mode"

    # Test filters
    assert len(request_dict["query"]["filters"]) == 3

    # Test quantitative filter
    quant_filter = request_dict["query"]["filters"][0]
    assert quant_filter["filterType"] == FilterType.QUANTITATIVE_NUMERICAL
    assert quant_filter["quantitativeFilterType"] == QuantitativeFilterType.RANGE
    assert quant_filter["min"] == 10
    assert quant_filter["max"] == 63
    assert quant_filter["field"]["fieldCaption"] == "Sales"
    assert quant_filter["field"]["function"] == Function.SUM

    # Test date filter
    date_filter = request_dict["query"]["filters"][1]
    assert date_filter["filterType"] == FilterType.DATE
    assert date_filter["periodType"] == PeriodType.MONTHS
    assert date_filter["dateRangeType"] == DateRangeType.NEXTN
    assert date_filter["rangeN"] == 3
    assert date_filter["anchorDate"] == datetime.date(2021, 1, 1)
    assert date_filter["field"]["fieldCaption"] == "Order Date"

    # Test set filter
    set_filter = request_dict["query"]["filters"][2]
    assert set_filter["filterType"] == FilterType.SET
    assert set_filter["values"] == ["First Class"]
    assert set_filter["exclude"] is False
    assert set_filter["field"]["fieldCaption"] == "Ship Mode"


def test_datasource_luid_not_required():
    """Test Datasource() with no fields is legal."""
    datasource = Datasource()
    assert datasource.datasourceLuid is None
    assert datasource.workbookDatasourceId is None


def test_datasource_workbook_datasource_id():
    """Test Datasource accepts workbookDatasourceId in lieu of datasourceLuid."""
    datasource = Datasource(workbookDatasourceId="sampleWorkbookDatasourceId")
    assert datasource.datasourceLuid is None
    assert datasource.workbookDatasourceId == "sampleWorkbookDatasourceId"


def test_query_request_with_workbook_datasource_id():
    """Test QueryRequest builds and serializes with workbookDatasourceId-only datasource."""
    request = QueryRequest(
        query=Query(fields=[DimensionField(fieldCaption="Category")]),
        datasource=Datasource(workbookDatasourceId="sampleWorkbookDatasourceId"),
    )
    request_dict = request.model_dump(exclude_none=True)
    assert request_dict["datasource"] == {
        "workbookDatasourceId": "sampleWorkbookDatasourceId"
    }
    assert "datasourceLuid" not in request_dict["datasource"]


def test_query_datasource_options_with_new_session():
    """Test QueryDatasourceOptions exposes the withNewSession flag."""
    options = QueryDatasourceOptions(withNewSession=True)
    assert options.withNewSession is True


def test_query_request_with_new_session_options():
    """Test QueryRequest serializes withNewSession when set on options."""
    request = QueryRequest(
        query=Query(fields=[DimensionField(fieldCaption="Category")]),
        datasource=Datasource(datasourceLuid="abc"),
        options=QueryDatasourceOptions(withNewSession=True),
    )
    request_dict = request.model_dump(exclude_none=True)
    assert request_dict["options"]["withNewSession"] is True


def test_period_type_unspecified_serializes_to_wire():
    """RelativeDateFilter accepts and serializes PeriodType.UNSPECIFIED literally."""
    filter_ = RelativeDateFilter(
        field=DimensionFilterField(fieldCaption="Order Date"),
        filterType=FilterType.DATE,
        periodType=PeriodType.UNSPECIFIED,
        dateRangeType=DateRangeType.CURRENT,
        anchorDate=datetime.date(2024, 1, 1),
    )
    assert filter_.periodType == PeriodType.UNSPECIFIED
    assert (
        filter_.model_dump(mode="json", exclude_none=True)["periodType"]
        == "UNSPECIFIED"
    )


def test_running_total_aggregation_unspecified_serializes_to_wire():
    """RunningTotalTableCalcSpecification serializes aggregation=UNSPECIFIED literally."""
    spec = RunningTotalTableCalcSpecification(
        tableCalcType=TableCalcType.RUNNING_TOTAL.value,
        dimensions=[TableCalcFieldReference(fieldCaption="Region")],
        aggregation=TableCalcComputedAggregation.UNSPECIFIED,
    )
    assert spec.aggregation == TableCalcComputedAggregation.UNSPECIFIED
    assert (
        spec.model_dump(mode="json", exclude_none=True)["aggregation"] == "UNSPECIFIED"
    )


def test_moving_aggregation_unspecified_serializes_to_wire():
    """MovingTableCalcSpecification serializes aggregation=UNSPECIFIED literally."""
    spec = MovingTableCalcSpecification(
        tableCalcType=TableCalcType.MOVING_CALCULATION.value,
        dimensions=[TableCalcFieldReference(fieldCaption="Region")],
        aggregation=TableCalcComputedAggregation.UNSPECIFIED,
    )
    assert spec.aggregation == TableCalcComputedAggregation.UNSPECIFIED
    assert (
        spec.model_dump(mode="json", exclude_none=True)["aggregation"] == "UNSPECIFIED"
    )


# --------------------------------------------------------------------------- #
# Workbook-datasource-id payloads + example wiring
# --------------------------------------------------------------------------- #


def _make_args(**kwargs):
    """Build a fake argparse.Namespace with sensible defaults for the
    workbook-datasource-id args."""
    defaults = {
        "workbook_datasource_id": None,
        "global_session_header": None,
        "x_session_id": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_simple_workbook_query_shape():
    query = create_simple_workbook_query()
    dumped = query.model_dump(mode="json", exclude_none=True)
    assert [f["fieldCaption"] for f in dumped["fields"]] == ["Category", "Sales"]
    sales = dumped["fields"][1]
    assert sales["function"] == Function.SUM.value
    # No filter/parameter/options on a simple workbook query.
    assert "filters" not in dumped
    assert "parameters" not in dumped


def test_workbook_custom_calculation_shape():
    query = create_workbook_custom_calculation()
    dumped = query.model_dump(mode="json", exclude_none=True)
    assert len(dumped["fields"]) == 1
    only_field = dumped["fields"][0]
    assert only_field["fieldCaption"] == "AOV"
    assert only_field["calculation"] == "SUM([Profit])/COUNTD([Order ID])"


def test_workbook_bin_formatting_with_parameter_shape():
    query = create_workbook_bin_formatting_with_parameter()
    dumped = query.model_dump(mode="json", exclude_none=True)
    assert dumped["fields"][0]["fieldCaption"] == "Profit (bin)"
    assert dumped["fields"][0]["sortPriority"] == 1
    assert dumped["parameters"] == [
        {"parameterCaption": "Profit Bin Size", "value": 50}
    ]


def test_workbook_new_bin_field_shape():
    query = create_workbook_new_bin_field()
    dumped = query.model_dump(mode="json", exclude_none=True)
    assert dumped["fields"][0]["fieldCaption"] == "Sales"
    assert dumped["fields"][0]["function"] == Function.SUM.value
    bin_field = dumped["fields"][1]
    assert bin_field["fieldCaption"] == "Profit"
    assert bin_field["binSize"] == 4000


def test_workbook_query_functions_registry_is_callable_and_unique():
    """Every entry in WORKBOOK_QUERY_FUNCTIONS returns a valid Query and the
    list contains no duplicates (each query function should appear at most
    once)."""
    assert len(WORKBOOK_QUERY_FUNCTIONS) == len(set(WORKBOOK_QUERY_FUNCTIONS))
    for func in WORKBOOK_QUERY_FUNCTIONS:
        result = func()
        assert isinstance(result, Query)
        assert result.fields  # at least one field


def test_workbook_query_request_uses_workbook_datasource_id():
    """A QueryRequest assembled the way the example runner does it should
    serialize with workbookDatasourceId and no datasourceLuid."""
    request = QueryRequest(
        query=create_simple_workbook_query(),
        datasource=common.create_workbook_datasource("wb-ds-abc"),
    )
    dumped = request.model_dump(mode="json", exclude_none=True)
    assert dumped["datasource"] == {"workbookDatasourceId": "wb-ds-abc"}
    assert "datasourceLuid" not in dumped["datasource"]


def test_workbook_datasource_args_complete_requires_all_three():
    assert not common.workbook_datasource_args_complete(_make_args())
    assert not common.workbook_datasource_args_complete(
        _make_args(workbook_datasource_id="x")
    )
    assert not common.workbook_datasource_args_complete(
        _make_args(workbook_datasource_id="x", global_session_header="y")
    )
    assert not common.workbook_datasource_args_complete(
        _make_args(workbook_datasource_id="x", x_session_id="z")
    )
    assert not common.workbook_datasource_args_complete(
        _make_args(global_session_header="y", x_session_id="z")
    )
    assert common.workbook_datasource_args_complete(
        _make_args(
            workbook_datasource_id="x",
            global_session_header="y",
            x_session_id="z",
        )
    )


def test_workbook_datasource_args_complete_rejects_empty_strings():
    """Empty strings should be treated as 'not provided' so we don't send blank
    header values."""
    assert not common.workbook_datasource_args_complete(
        _make_args(
            workbook_datasource_id="x",
            global_session_header="",
            x_session_id="z",
        )
    )
    assert not common.workbook_datasource_args_complete(
        _make_args(
            workbook_datasource_id="",
            global_session_header="y",
            x_session_id="z",
        )
    )


def test_workbook_datasource_args_complete_rejects_whitespace_strings():
    """Whitespace-only strings should also count as 'not provided' so the user
    can't accidentally activate the workbook path with a blank-looking value."""
    assert not common.workbook_datasource_args_complete(
        _make_args(
            workbook_datasource_id="x",
            global_session_header="   ",
            x_session_id="z",
        )
    )
    assert not common.workbook_datasource_args_complete(
        _make_args(
            workbook_datasource_id="\t\n",
            global_session_header="y",
            x_session_id="z",
        )
    )


def test_workbook_session_headers_uses_documented_names():
    args = _make_args(
        workbook_datasource_id="wb-ds",
        global_session_header="gsh-value",
        x_session_id="sid-value",
    )
    headers = common.workbook_session_headers(args)
    assert headers == {
        "Global-Session-Header": "gsh-value",
        "X-Session-Id": "sid-value",
    }


def test_workbook_session_headers_strips_surrounding_whitespace():
    """Leading/trailing spaces and tabs are stripped; embedded CR/LF/NUL
    would be rejected separately by _validate_header_value."""
    args = _make_args(
        workbook_datasource_id="wb-ds",
        global_session_header="  gsh-value\t",
        x_session_id="  sid-value  ",
    )
    headers = common.workbook_session_headers(args)
    assert headers == {
        "Global-Session-Header": "gsh-value",
        "X-Session-Id": "sid-value",
    }


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("global_session_header", "value\r\nInjected: bad"),
        ("global_session_header", "value\rstill-bad"),
        ("global_session_header", "value\nstill-bad"),
        ("global_session_header", "value\x00with-nul"),
        ("x_session_id", "id\r\nInjected: bad"),
        ("x_session_id", "id\x00bad"),
    ],
)
def test_workbook_session_headers_rejects_crlf_and_nul(field, bad_value):
    args = _make_args(
        workbook_datasource_id="wb-ds",
        global_session_header="ok",
        x_session_id="ok",
    )
    setattr(args, field, bad_value)
    with pytest.raises(ValueError, match="CR, LF, or NUL"):
        common.workbook_session_headers(args)


def test_print_help_describes_workbook_args_as_additional(capsys):
    """print_help() must describe --workbook-datasource-id as running an
    additional set of queries, not replacing the LUID-based examples — the
    runner does both."""
    common.print_help()
    out = capsys.readouterr().out
    assert "--workbook-datasource-id" in out
    assert "--global-session-header" in out
    assert "--x-session-id" in out
    assert "in lieu of" not in out
    assert "additional set of queries" in out


@pytest.mark.parametrize(
    "func",
    [
        create_simple_workbook_query,
        create_workbook_custom_calculation,
        create_workbook_bin_formatting_with_parameter,
        create_workbook_new_bin_field,
    ],
)
def test_workbook_query_request_keeps_workbook_id_off_query(func):
    """For every workbook payload, the assembled QueryRequest must place
    workbookDatasourceId on the datasource (not on the query) and must never
    expose datasourceLuid."""
    request = QueryRequest(
        query=func(),
        datasource=common.create_workbook_datasource("wb-ds-xyz"),
    )
    dumped = request.model_dump(mode="json", exclude_none=True)
    assert dumped["datasource"] == {"workbookDatasourceId": "wb-ds-xyz"}
    assert "datasourceLuid" not in dumped["datasource"]
    # workbookDatasourceId must NOT appear anywhere inside the query body.
    import json as _json

    assert "workbookDatasourceId" not in _json.dumps(dumped["query"])


def test_create_workbook_datasource_sets_only_workbook_id():
    ds = common.create_workbook_datasource("wb-ds-xyz")
    assert isinstance(ds, Datasource)
    assert ds.workbookDatasourceId == "wb-ds-xyz"
    assert ds.datasourceLuid is None


def test_workbook_payloads_are_distinct_from_datasource_luid_payloads():
    """The new workbook payloads should be separate function objects from the
    existing datasource-luid payloads — that's what lets the example runner
    pick the right set for each codepath without surprising name collisions."""
    from src.examples.payload import QUERY_FUNCTIONS

    overlap = set(WORKBOOK_QUERY_FUNCTIONS) & set(QUERY_FUNCTIONS)
    assert overlap == set()
