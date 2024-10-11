from pydantic import BaseModel


class UserModel(BaseModel):
    user_id: int
    username: str