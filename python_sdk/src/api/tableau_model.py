from pydantic import BaseModel, ConfigDict


class TableauModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
