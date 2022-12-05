from http.client import HTTPException
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
from typing import List,Optional
from fastapi.encoders import jsonable_encoder

import logging

from pydantic import BaseModel

app = FastAPI(title="Store Application",
    description="Sample FastAPI Application with Swagger and Sqlalchemy",
    version="1.0.0",)


SQLALCHEMY_DATABASE_URL = "sqlite:///./data/app.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

logger_app = logging.getLogger("uvicorn.app")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== models
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False, unique=True,index=True)
    price = Column(Float(precision=2), nullable=False)
    description = Column(String(200))
    store_id = Column(Integer,ForeignKey('stores.id'),nullable=False)
    def __repr__(self):
        return 'ItemModel(name=%s, price=%s,store_id=%s)' % (self.name, self.price,self.store_id)
    
class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False, unique=True)
    items = relationship("Item",primaryjoin="Store.id == Item.store_id",cascade="all, delete-orphan")

    def __repr__(self):
        return 'Store(name=%s)' % self.name


# ===== schemas
class ItemBaseSchema(BaseModel):
    name: str
    price : float
    description: Optional[str] = None
    store_id: int


class ItemCreateSchema(ItemBaseSchema):
    pass


class ItemSchema(ItemBaseSchema):
    id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StoreBaseSchema(BaseModel):
    name: str

class StoreCreateSchema(StoreBaseSchema):
    pass

class StoreSchema(StoreBaseSchema):
    id: int
    items: List[ItemSchema] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# ===== repos
class ItemRepo:
    
 async def create(db: Session, item: ItemCreateSchema):
        db_item = Item(name=item.name,price=item.price,description=item.description,store_id=item.store_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
 def fetch_by_id(db: Session,_id):
     return db.query(Item).filter(Item.id == _id).first()
 
 def fetch_by_name(db: Session,name):
     return db.query(Item).filter(Item.name == name).first()
 
 def fetch_all(db: Session, skip: int = 0, limit: int = 100):
     return db.query(Item).offset(skip).limit(limit).all()
 
 async def delete(db: Session,item_id):
     db_item= db.query(Item).filter_by(id=item_id).first()
     db.delete(db_item)
     db.commit()
     
     
 async def update(db: Session,item_data):
    updated_item = db.merge(item_data)
    db.commit()
    return updated_item
    
    
    
class StoreRepo:
    
    async def create(db: Session, store: StoreCreateSchema):
            db_store = Store(name=store.name)
            db.add(db_store)
            db.commit()
            db.refresh(db_store)
            return db_store
        
    def fetch_by_id(db: Session,_id:int):
        return db.query(Store).filter(Store.id == _id).first()
    
    def fetch_by_name(db: Session,name:str):
        return db.query(Store).filter(Store.name == name).first()
    
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Store).offset(skip).limit(limit).all()
    
    async def delete(db: Session,_id:int):
        db_store= db.query(Store).filter_by(id=_id).first()
        db.delete(db_store)
        db.commit()
        
    async def update(db: Session,store_data):
        db.merge(store_data)
        db.commit()

Base.metadata.create_all(bind=engine)

@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})

@app.post('/items', tags=["Item"],response_model=ItemSchema,status_code=201)
async def create_item(item_request: ItemCreateSchema, db: Session = Depends(get_db)):
    """
    Create an Item and store it in the database
    """
    
    db_item = ItemRepo.fetch_by_name(db, name=item_request.name)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists!")

    return await ItemRepo.create(db=db, item=item_request)

@app.get('/items', tags=["Item"],response_model=List[ItemSchema])
def get_all_items(name: Optional[str] = None,db: Session = Depends(get_db)):
    """
    Get all the Items stored in database
    """
    if name:
        items =[]
        db_item = ItemRepo.fetch_by_name(db,name)
        items.append(db_item)
        return items
    else:
        return ItemRepo.fetch_all(db)


@app.get('/items/{item_id}', tags=["Item"],response_model=ItemSchema)
def get_item(item_id: int,db: Session = Depends(get_db)):
    """
    Get the Item with the given ID provided by User stored in database
    """
    db_item = ItemRepo.fetch_by_id(db,item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found with the given ID")
    return db_item

@app.delete('/items/{item_id}', tags=["Item"])
async def delete_item(item_id: int,db: Session = Depends(get_db)):
    """
    Delete the Item with the given ID provided by User stored in database
    """
    db_item = ItemRepo.fetch_by_id(db,item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found with the given ID")
    await ItemRepo.delete(db,item_id)
    return "Item deleted successfully!"

@app.put('/items/{item_id}', tags=["Item"],response_model=ItemSchema)
async def update_item(item_id: int,item_request: ItemSchema, db: Session = Depends(get_db)):
    """
    Update an Item stored in the database
    """
    db_item = ItemRepo.fetch_by_id(db, item_id)
    if db_item:
        update_item_encoded = jsonable_encoder(item_request)
        db_item.name = update_item_encoded['name']
        db_item.price = update_item_encoded['price']
        db_item.description = update_item_encoded['description']
        db_item.store_id = update_item_encoded['store_id']
        return await ItemRepo.update(db=db, item_data=db_item)
    else:
        raise HTTPException(status_code=400, detail="Item not found with the given ID")


@app.post('/stores', tags=["Store"],response_model=StoreSchema, status_code=201)
async def create_store(store_request: StoreCreateSchema, db: Session = Depends(get_db)):
    """
    Create a Store and save it in the database
    """
    db_store = StoreRepo.fetch_by_name(db, name=store_request.name)
    print(db_store)
    if db_store:
        raise HTTPException(status_code=400, detail="Store already exists!")

    return await StoreRepo.create(db=db, store=store_request)

@app.get('/stores', tags=["Store"],response_model=List[StoreSchema])
def get_all_stores(name: Optional[str] = None,db: Session = Depends(get_db)):
    """
    Get all the Stores stored in database
    """
    if name:
        stores =[]
        db_store = StoreRepo.fetch_by_name(db,name)
        print(db_store)
        stores.append(db_store)
        return stores
    else:
        return StoreRepo.fetch_all(db)
    
@app.get('/stores/{store_id}', tags=["Store"],response_model=StoreSchema)
def get_store(store_id: int,db: Session = Depends(get_db)):
    """
    Get the Store with the given ID provided by User stored in database
    """
    db_store = StoreRepo.fetch_by_id(db,store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found with the given ID")
    return db_store

@app.delete('/stores/{store_id}', tags=["Store"])
async def delete_store(store_id: int,db: Session = Depends(get_db)):
    """
    Delete the Item with the given ID provided by User stored in database
    """
    db_store = StoreRepo.fetch_by_id(db,store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found with the given ID")
    await StoreRepo.delete(db,store_id)
    return "Store deleted successfully!"
    

@app.get("/")
async def root():
    return {"message": "hello world again"}


if __name__ == "__main__":
    uvicorn.run("app:app", port=5003, reload=True)    