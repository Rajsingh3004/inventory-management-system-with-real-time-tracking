from pydantic import BaseModel

class UserSchema(BaseModel):
   
    name:str
    email:str
    password:str
    role:str
    
    
class ItemSchema(BaseModel):
    
    name:str
    quantity:int
    price:int
    

class RequestSchema(BaseModel):
    reqitem_id: int
    quantity: int
    address: str   # ✅ NEW
    
class Login(BaseModel):
    
    username:str
    password:str


class SaleSchema(BaseModel):
    reqitem_id:str
    name:str
    status:str
    price:int


 