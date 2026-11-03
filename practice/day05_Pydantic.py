from pydantic import BaseModel, Field,field_validator
from typing import Optional


class User(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=20)
    age: int = Field(default=18, ge=0, l=120)
    email: Optional[str] = None

    @field_validator("age")
    @classmethod
    def check_age(cls,value):
        if value<0:
            raise ValueError("年龄不能小于0")
        return value


user=User(id=1,name="张三",age=10)

print(user.name)

print(user.model_dump())

print(user.model_dump_json())


data = {
    "id": "100",
    "name": "张三",
    "age": 130
}

user=User.model_validate(data)
print(user.id)
print(user.model_dump())



class Item(BaseModel):
    name:str
    price:float
class Order(BaseModel):
    order_id:int
    items:list[Item]
order = Order(
    order_id=1,
    items=[
        {"name": "商品A", "price": 100},
        {"name": "商品B", "price": 200}
    ]
)
print(order.model_dump())

