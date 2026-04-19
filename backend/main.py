from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from model import Item, Request, User, Base, Sale 
from schema import UserSchema, RequestSchema, ItemSchema
from auth import hashed_pass, verify_password, create_jwt, get_current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 1. Database URL define karein
DATABASE_URL = "mysql+pymysql://root:raj123@localhost:3306/inventory_db"

# 2. Engine create karein
engine = create_engine(DATABASE_URL)
# Yeh line ensure karti hai ki agar table nahi hai, toh wo ban jaye
Base.metadata.create_all(bind=engine)
# 3. sessionLocal yahan define hota hai (Yahi main.py mein import hota hai)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# DB Dependency
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTH ENDPOINTS ---

@app.post("/register", tags=["auth"])
def register(user: UserSchema, db: Session = Depends(get_db)):
    # Check if user exists first
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pass(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login", tags=["auth"]) 
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.username).first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_jwt(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "role": user.role
    }

# --- ITEM ENDPOINTS ---

@app.post("/item", tags=["admin"])
def create_item(item: ItemSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    new_item = Item(name=item.name, quantity=item.quantity, price=item.price)
    db.add(new_item)
    db.commit()
    return {"message": "Item added successfully"}

@app.get("/show", tags=["user", "admin"])
def show_items(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Simple role check
    return db.query(Item).all()

# --- REQUEST ENDPOINTS ---

# --- REQUEST ENDPOINTS ---

@app.post("/request", tags=["user"])
def create_request(request: RequestSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    item = db.query(Item).filter(Item.id == request.reqitem_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    new_request = Request(
        reqitem_id=request.reqitem_id,
        quantity=request.quantity,
        price=item.price, # Item table se price uthao
        status="pending"
    )
    db.add(new_request)
    db.commit()
    return {"message": "Request submitted successfully"}

@app.put("/update_request/{id}")
def update_request(id: int, status_data: dict, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    new_status = status_data.get("status").lower()
    req.status = new_status
    
    # Yahan se "approved" wala stock minus logic hata diya gaya hai 
    # Kyunki ab wo kaam /approval endpoint karega.
    
    db.commit()
    return {"message": f"Status updated to {new_status}"}

@app.get("/show_requests") 
def show_requests(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Request).all()

@app.put("/update/{item_id}")
async def update_item(item_id: int, item_data: ItemSchema, db: Session = Depends(get_db)):
    # 1. Fetch
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item ID not found!")

    # 2. Explicit Update
    db_item.name = item_data.name
    db_item.quantity = item_data.quantity  # Ensure this is being updated
    db_item.price = item_data.price

    # 3. Commit
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Updated!", "data": db_item}



from datetime import datetime

@app.post("/approval/{request_id}", tags=["admin"])
def request_approval(request_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # 1. Request find karein
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check karein agar pehle se approved/rejected hai
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    # 2. Item check karein
    item = db.query(Item).filter(Item.id == req.reqitem_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found") 

    # 3. Stock Check
    if item.quantity < req.quantity:
        req.status = "rejected"
        db.commit()
        return {"message": "Insufficient stock, request rejected"}

    # --- LOGIC START: Approval + Auto-Sync to Sales ---
    
    # A. Stock update karein
    item.quantity -= req.quantity
    req.status = "approved"

    # B. Sale table mein entry karein (Current Time aur Week ke saath)
    now = datetime.now()
    new_sale = Sale(
        request_id=req.id,
        reqitem_id=req.reqitem_id,
        quantity=req.quantity,
        price=req.price,
        created_at=now,
        week_number=now.isocalendar()[1] # ISO week number nikalta hai (1-52)
    )
    
    db.add(new_sale)
    
    # C. Final Commit (Dono table ek saath update honge)
    try:
        db.commit()
        return {"message": "Request approved and record added to Sales table"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during sync")
@app.delete("/delete/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        db.rollback()
        # Yeh error tab aati hai jab Item kisi doosri table mein refer ho raha ho
        raise HTTPException(
            status_code=400, 
            detail="Pehle is item se judi saari Requests aur Sales records delete karein."
        )
    
@app.delete("/delete_request/{request_id}", tags=["admin"])
def delete_request(request_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 1. Security Check: Sirf admin delete kar sake
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required to delete requests")

    # 2. Find the request
    req = db.query(Request).filter(Request.id == request_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    try:
        # 3. Database se delete karein
        db.delete(req)
        db.commit()
        return {"status": "Success", "message": f"Request ID {request_id} has been deleted."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete request. It might be linked to other records (like Sales)."
        )   


@app.get("/sales", tags=["admin"])
def get_sales(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return db.query(Sale).all()        