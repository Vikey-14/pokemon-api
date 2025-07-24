# models/pokemon.py

from pydantic import BaseModel, Field

class Pokemon(BaseModel):
    name: str = Field(..., alias="poke_name", description="Name of the Pokémon")
    level: int = Field(..., ge=5, le=100, description="Level must be between 5 and 100")
    ptype: str = Field(..., alias="Type", description="Type of the Pokémon")
