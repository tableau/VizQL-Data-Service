import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.filter_filter_type import FilterFilterType
from ..models.quantitative_filter_base_quantitative_filter_type import QuantitativeFilterBaseQuantitativeFilterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.filter_field_with_calculation import FilterFieldWithCalculation
    from ..models.filter_field_with_caption import FilterFieldWithCaption
    from ..models.filter_field_with_caption_function import FilterFieldWithCaptionFunction


T = TypeVar("T", bound="QuantitativeDateFilter")


@_attrs_define
class QuantitativeDateFilter:
    """
    Attributes:
        field (Union['FilterFieldWithCalculation', 'FilterFieldWithCaption', 'FilterFieldWithCaptionFunction']):
        filter_type (FilterFilterType):
        quantitative_filter_type (QuantitativeFilterBaseQuantitativeFilterType):
        context (Union[Unset, bool]): Make the given filter a context filter, meaning that it's an independent filter.
            Any other filters that you set are defined as dependent filters because they process only the data that passes
            through the context filter. Default: False.
        include_nulls (Union[Unset, bool]): Should nulls be returned or not. Only applies to RANGE, MIN, and MAX
            filters. If not provided, the default is to not include null values.
        min_date (Union[Unset, datetime.date]): An RFC 3339 date indicating the earliest date to filter upon. Required
            if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN.
        max_date (Union[Unset, datetime.date]): An RFC 3339 date indicating the latest date to filter on. Required if
            using quantitativeFilterType RANGE or if using quantitativeFilterType MIN.
    """

    field: Union["FilterFieldWithCalculation", "FilterFieldWithCaption", "FilterFieldWithCaptionFunction"]
    filter_type: FilterFilterType
    quantitative_filter_type: QuantitativeFilterBaseQuantitativeFilterType
    context: Union[Unset, bool] = False
    include_nulls: Union[Unset, bool] = UNSET
    min_date: Union[Unset, datetime.date] = UNSET
    max_date: Union[Unset, datetime.date] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.filter_field_with_caption import FilterFieldWithCaption
        from ..models.filter_field_with_caption_function import FilterFieldWithCaptionFunction

        field: dict[str, Any]
        if isinstance(self.field, FilterFieldWithCaption):
            field = self.field.to_dict()
        elif isinstance(self.field, FilterFieldWithCaptionFunction):
            field = self.field.to_dict()
        else:
            field = self.field.to_dict()

        filter_type = self.filter_type.value

        quantitative_filter_type = self.quantitative_filter_type.value

        context = self.context

        include_nulls = self.include_nulls

        min_date: Union[Unset, str] = UNSET
        if not isinstance(self.min_date, Unset):
            min_date = self.min_date.isoformat()

        max_date: Union[Unset, str] = UNSET
        if not isinstance(self.max_date, Unset):
            max_date = self.max_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "filterType": filter_type,
                "quantitativeFilterType": quantitative_filter_type,
            }
        )
        if context is not UNSET:
            field_dict["context"] = context
        if include_nulls is not UNSET:
            field_dict["includeNulls"] = include_nulls
        if min_date is not UNSET:
            field_dict["minDate"] = min_date
        if max_date is not UNSET:
            field_dict["maxDate"] = max_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.filter_field_with_calculation import FilterFieldWithCalculation
        from ..models.filter_field_with_caption import FilterFieldWithCaption
        from ..models.filter_field_with_caption_function import FilterFieldWithCaptionFunction

        d = dict(src_dict)

        def _parse_field(
            data: object,
        ) -> Union["FilterFieldWithCalculation", "FilterFieldWithCaption", "FilterFieldWithCaptionFunction"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_filter_field_type_0 = FilterFieldWithCaption.from_dict(data)

                return componentsschemas_filter_field_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_filter_field_type_1 = FilterFieldWithCaptionFunction.from_dict(data)

                return componentsschemas_filter_field_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_filter_field_type_2 = FilterFieldWithCalculation.from_dict(data)

            return componentsschemas_filter_field_type_2

        field = _parse_field(d.pop("field"))

        filter_type = FilterFilterType(d.pop("filterType"))

        quantitative_filter_type = QuantitativeFilterBaseQuantitativeFilterType(d.pop("quantitativeFilterType"))

        context = d.pop("context", UNSET)

        include_nulls = d.pop("includeNulls", UNSET)

        _min_date = d.pop("minDate", UNSET)
        min_date: Union[Unset, datetime.date]
        if isinstance(_min_date, Unset):
            min_date = UNSET
        else:
            min_date = isoparse(_min_date).date()

        _max_date = d.pop("maxDate", UNSET)
        max_date: Union[Unset, datetime.date]
        if isinstance(_max_date, Unset):
            max_date = UNSET
        else:
            max_date = isoparse(_max_date).date()

        quantitative_date_filter = cls(
            field=field,
            filter_type=filter_type,
            quantitative_filter_type=quantitative_filter_type,
            context=context,
            include_nulls=include_nulls,
            min_date=min_date,
            max_date=max_date,
        )

        quantitative_date_filter.additional_properties = d
        return quantitative_date_filter

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
