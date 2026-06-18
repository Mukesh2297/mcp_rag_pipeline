from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    content: str

    model_config = {
        "from_attributes": True
    }