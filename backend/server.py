from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import hashlib
import jwt
from passlib.context import CryptContext
import base64
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="HANNU CLOTHES API", description="E-commerce API for women's clothing")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hannu-clothes-secret-key-2024")

# Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: int  # Price in COP cents
    category: str  # dresses, tops, bottoms, accessories
    image: str
    composition: str
    care: str
    sizes: List[str]
    stock: dict = Field(default_factory=dict)  # size -> quantity
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    category: str
    image: str
    composition: str
    care: str
    sizes: List[str]
    stock: dict = Field(default_factory=dict)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category: Optional[str] = None
    image: Optional[str] = None
    composition: Optional[str] = None
    care: Optional[str] = None
    sizes: Optional[List[str]] = None
    stock: Optional[dict] = None

class CartItem(BaseModel):
    product_id: str
    name: str
    price: int
    size: str
    quantity: int
    image: str

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    document_type: str  # CC, CE, TI, PP, NIT
    document_number: str
    items: List[CartItem]
    subtotal: int
    shipping: int
    total: int
    status: str = "pending"  # pending, paid, processing, shipped, delivered, cancelled
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    shipping_address: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    document_type: str
    document_number: str
    items: List[CartItem]
    shipping_address: dict

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    admin = await db.admins.find_one({"username": username})
    if admin is None:
        raise HTTPException(status_code=401, detail="Admin not found")
    
    return Admin(**admin)

def validate_colombian_document(document_type: str, document_number: str) -> bool:
    """Validate Colombian identification documents"""
    document_number = re.sub(r'[^\d]', '', document_number)
    
    if document_type == "CC":  # Cédula de Ciudadanía
        return 6 <= len(document_number) <= 10 and document_number.isdigit()
    elif document_type == "CE":  # Cédula de Extranjería
        return 6 <= len(document_number) <= 12 and document_number.isdigit()
    elif document_type == "TI":  # Tarjeta de Identidad
        return 8 <= len(document_number) <= 11 and document_number.isdigit()
    elif document_type == "PP":  # Pasaporte
        return 6 <= len(document_number) <= 20
    elif document_type == "NIT":  # Número de Identificación Tributaria
        return 8 <= len(document_number) <= 15 and document_number.isdigit()
    
    return False

# Routes
@api_router.get("/")
async def root():
    return {"message": "HANNU CLOTHES API - Fashion for the modern woman"}

# Product routes
@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, limit: int = 50):
    """Get all products or filter by category"""
    query = {}
    if category and category != "all":
        query["category"] = category
    
    products = await db.products.find(query).limit(limit).to_list(limit)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product)

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, admin: Admin = Depends(get_current_admin)):
    """Create a new product (admin only)"""
    product_dict = product.dict()
    product_obj = Product(**product_dict)
    
    await db.products.insert_one(product_obj.dict())
    return product_obj

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, admin: Admin = Depends(get_current_admin)):
    """Update a product (admin only)"""
    existing_product = await db.products.find_one({"id": product_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    
    updated_product = await db.products.find_one({"id": product_id})
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin: Admin = Depends(get_current_admin)):
    """Delete a product (admin only)"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# Order routes
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    """Create a new order"""
    # Validate Colombian document
    if not validate_colombian_document(order_data.document_type, order_data.document_number):
        raise HTTPException(status_code=400, detail="Invalid Colombian document")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order_data.items)
    shipping = 0 if subtotal >= 150000 else 15000  # Free shipping over 150,000 COP
    total = subtotal + shipping
    
    # Create order
    order_dict = order_data.dict()
    order_dict.update({
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total
    })
    
    order_obj = Order(**order_dict)
    await db.orders.insert_one(order_obj.dict())
    
    return order_obj

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get order details"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return Order(**order)

@api_router.get("/orders", response_model=List[Order])
async def get_orders(admin: Admin = Depends(get_current_admin), limit: int = 50):
    """Get all orders (admin only)"""
    orders = await db.orders.find().sort("created_at", -1).limit(limit).to_list(limit)
    return [Order(**order) for order in orders]

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, admin: Admin = Depends(get_current_admin)):
    """Update order status (admin only)"""
    valid_statuses = ["pending", "paid", "processing", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.orders.update_one(
        {"id": order_id}, 
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated successfully"}

# Admin routes
@api_router.post("/admin/register", response_model=dict)
async def register_admin(admin_data: AdminCreate):
    """Register a new admin"""
    # Check if admin already exists
    existing_admin = await db.admins.find_one({"$or": [{"username": admin_data.username}, {"email": admin_data.email}]})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    # Hash password
    hashed_password = hash_password(admin_data.password)
    
    # Create admin
    admin_dict = admin_data.dict()
    admin_dict["password_hash"] = hashed_password
    del admin_dict["password"]
    
    admin_obj = Admin(**admin_dict)
    await db.admins.insert_one(admin_obj.dict())
    
    return {"message": "Admin registered successfully"}

@api_router.post("/admin/login", response_model=Token)
async def login_admin(login_data: AdminLogin):
    """Admin login"""
    admin = await db.admins.find_one({"username": login_data.username})
    if not admin or not verify_password(login_data.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not admin["is_active"]:
        raise HTTPException(status_code=401, detail="Admin account is inactive")
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/admin/me", response_model=dict)
async def get_admin_profile(admin: Admin = Depends(get_current_admin)):
    """Get current admin profile"""
    return {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
        "created_at": admin.created_at,
        "is_active": admin.is_active
    }

# Categories route
@api_router.get("/categories")
async def get_categories():
    """Get product categories"""
    return [
        {"id": "all", "name": "Todo"},
        {"id": "dresses", "name": "Vestidos"},
        {"id": "tops", "name": "Blusas"},
        {"id": "bottoms", "name": "Pantalones"},
        {"id": "accessories", "name": "Accesorios"}
    ]

# Analytics routes (admin only)
@api_router.get("/analytics/overview")
async def get_analytics_overview(admin: Admin = Depends(get_current_admin)):
    """Get basic analytics overview"""
    total_products = await db.products.count_documents({})
    total_orders = await db.orders.count_documents({})
    pending_orders = await db.orders.count_documents({"status": "pending"})
    
    # Calculate total revenue (from paid orders)
    pipeline = [
        {"$match": {"status": {"$in": ["paid", "processing", "shipped", "delivered"]}}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("HANNU CLOTHES API starting up...")
    
    # Create default admin if none exists
    admin_count = await db.admins.count_documents({})
    if admin_count == 0:
        default_admin = Admin(
            username="admin",
            email="admin@hannuclothes.com",
            password_hash=hash_password("admin123")
        )
        await db.admins.insert_one(default_admin.dict())
        logger.info("Default admin created: username=admin, password=admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()