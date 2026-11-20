from pydantic import BaseModel, ConfigDict


class ModeloBase(BaseModel):
    """Base de todos los modelos: limpia espacios sobrantes en los textos."""

    model_config = ConfigDict(str_strip_whitespace=True)
