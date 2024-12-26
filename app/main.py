from fastapi import FastAPI, Depends


from sqlalchemy import create_engine, Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy import text

from pydantic import BaseModel
from .database import get_db

class PostUser(BaseModel):
    email:str
    name:str

class PostOrder(BaseModel):
    id:int
    email:str
    food_name:str
    quantity:int


app = FastAPI()




@app.post("/create")
async def create_user(payload:PostUser, db:Session=Depends(get_db)):
    query = text(f"insert into users (email, name) values (:email, :name)")

    db.execute(query, dict(payload))
    db.commit()






@app.post("/order")
async def create_order(payload:PostOrder, db:Session=Depends(get_db)):
    temp = dict(payload)
    query_find_item = text("select * from fooditems where item_name = :item_name")

    buffer1 = db.execute(query_find_item, {"item_name": temp['food_name']})
    result1 = buffer1.fetchone()

    order = {
        "id": temp['id'], 
        "email": temp['email'],
        "item_id": result1[0],
        "food_name": temp['food_name'],
        "quantity": temp['quantity'],
        "total_price": temp['quantity']*result1[2]
    }

    query_insert_order = text(f"insert into orders (id, email, item_id, food_name, quantity, total_price) values (:id, :email, :item_id, :food_name,:quantity, :total_price)")

    db.execute(query_insert_order, order)
    db.commit()

    query_status_table = text(f"insert into orderstatus (order_id, status, total) values (:order_id, :status, :total)")

    db.execute(query_status_table, {"order_id":order['id'], "status": "pending", "total": order['total_price']})

    db.commit()

   
    
   

    return {"msg":"order submited!"}

