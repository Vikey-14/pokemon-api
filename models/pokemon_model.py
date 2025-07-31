from pydantic import BaseModel, Field
from typing import Optional
from pydantic import ConfigDict

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name", description="Name of the Pokémon")
    level: int = Field(..., ge=5, le=100, description="Level must be between 5 and 100")
    ptype: str = Field(..., description="Type of the Pokémon")  
    nickname: Optional[str] = Field(None, description="Optional nickname")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "poke_name": "Charizard",  
                "level": 50,
                "ptype": "Fire/Flying",
                "nickname": "Blazer"
            }
        },
        populate_by_name=True  # ✅ This enables internal access via `.name`
    )

class PatchPokemon(BaseModel):
    level: Optional[int] = Field(None, ge=5, le=100)
    ptype: Optional[str] = Field(None)
    nickname: Optional[str] = Field(None)
