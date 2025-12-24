from pydantic import BaseModel, Field
from typing import List, Tuple

class ImageClick(BaseModel):
    image_id: str
    point: Tuple[int, int]

class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    level1_images: List[str]
    level2_clicks: List[ImageClick]
    level3_sequence: List[str]
class LoginL1Request(BaseModel):
    username: str
    level1_images: List[str]

class LoginL2Request(BaseModel):
    username: str
    level2_clicks: List[ImageClick]

class LoginL3Request(BaseModel):
    username: str
    level3_sequence: List[str]

class ApiResponse(BaseModel):
    ok: bool
    message: str
