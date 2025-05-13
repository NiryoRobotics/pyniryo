from pydantic import BaseModel, RootModel, EmailStr
from .models_gen import User, Token

# pip install datamodel-code-generator
# datamodel-codegen --input ~/git/apiserver/doc/openapi.yml  --output ~/git/pyniryo/pyniryo/nate/models/models_gen.py --output-model-type pydantic_v2.BaseModel --input-file-type openapi


class UserEvent(BaseModel):
    pass


UserLoggedIn = UserEvent
UserLoggedOut = UserEvent

UserList = RootModel[list[User]]
TokenList = RootModel[list[Token]]
