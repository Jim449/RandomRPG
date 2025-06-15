from pydantic import BaseModel, ConfigDict


class BlueprintSchema(BaseModel):
    id: int
    name: str
    area_length: int
    area_count: int
    randomize_areas: bool

    model_config = ConfigDict(
        from_attributes=True
    )
