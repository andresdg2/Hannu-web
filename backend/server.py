from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Union
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
app = FastAPI(title="HANNU CLOTHES CATALOG API", description="Professional catalog system for women's clothing")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hannu-clothes-catalog-secret-key-2024")

# Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    retail_price: int  # Price in COP cents for retail customers
    wholesale_price: int  # Price in COP cents for wholesale customers
    category: str  # vestidos, enterizos, conjuntos, blusas, faldas, pantalones
    image: str  # Keep for backward compatibility
    images: List[str] = Field(default_factory=list)  # Support multiple images
    colors: List[str] = Field(default_factory=list)  # Support multiple colors
    specifications: str = ""
    composition: str = ""
    care: str = ""
    shipping_policy: str = ""
    exchange_policy: str = ""
    sizes: List[str] = Field(default_factory=list)
    stock: Dict[str, int] = Field(default_factory=dict)  # size -> quantity
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    retail_price: int
    wholesale_price: int
    category: str
    image: Optional[str] = ""  # Keep for backward compatibility
    images: List[str] = Field(default_factory=list)  # Support multiple images
    colors: List[str] = Field(default_factory=list)  # Support multiple colors
    specifications: Optional[str] = ""
    composition: Optional[str] = ""
    care: Optional[str] = ""
    shipping_policy: Optional[str] = ""
    exchange_policy: Optional[str] = ""
    sizes: List[str] = Field(default_factory=list)
    stock: Optional[Dict[str, int]] = Field(default_factory=dict)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    retail_price: Optional[int] = None
    wholesale_price: Optional[int] = None
    category: Optional[str] = None
    image: Optional[str] = None  # Keep for backward compatibility
    images: Optional[List[str]] = None  # Support multiple images
    colors: Optional[List[str]] = None  # Support multiple colors
    specifications: Optional[str] = None
    composition: Optional[str] = None
    care: Optional[str] = None
    shipping_policy: Optional[str] = None
    exchange_policy: Optional[str] = None
    sizes: Optional[List[str]] = None
    stock: Optional[Dict[str, int]] = None

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

class CatalogStats(BaseModel):
    total_products: int
    products_by_category: Dict[str, int]
    total_stock_value_retail: int
    total_stock_value_wholesale: int
    low_stock_products: List[str]

class StockUpdate(BaseModel):
    size: str
    quantity: int

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

# Routes
@api_router.get("/")
async def root():
    return {"message": "HANNU CLOTHES CATALOG API - Professional catalog system for women's fashion"}

# Product routes
@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, limit: int = 100):
    """Get all products or filter by category"""
    query = {}
    if category and category != "todos":
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
    # Validate category
    valid_categories = ["vestidos", "enterizos", "conjuntos", "blusas", "tops", "faldas", "pantalones"]
    if product.category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate prices
    if product.wholesale_price >= product.retail_price:
        raise HTTPException(status_code=400, detail="Wholesale price must be less than retail price")
    
    product_dict = product.dict()
    
    # Handle backward compatibility: if no images array but has image, add to images
    if not product_dict.get("images") and product_dict.get("image"):
        product_dict["images"] = [product_dict["image"]]
    elif product_dict.get("images") and not product_dict.get("image"):
        # Set first image as main image for backward compatibility
        product_dict["image"] = product_dict["images"][0] if product_dict["images"] else ""
    
    # Filter out empty strings from images and colors
    if product_dict.get("images"):
        product_dict["images"] = [img for img in product_dict["images"] if img.strip()]
    if product_dict.get("colors"):
        product_dict["colors"] = [color for color in product_dict["colors"] if color.strip()]
    
    product_obj = Product(**product_dict)
    
    # Convert to dict for MongoDB storage
    product_doc = product_obj.dict()
    await db.products.insert_one(product_doc)
    
    return product_obj

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, admin: Admin = Depends(get_current_admin)):
    """Update a product (admin only)"""
    existing_product = await db.products.find_one({"id": product_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Validate category if provided
    if "category" in update_data:
        valid_categories = ["vestidos", "enterizos", "conjuntos", "blusas", "faldas", "pantalones"]
        if update_data["category"] not in valid_categories:
            raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate prices if provided
    retail_price = update_data.get("retail_price", existing_product["retail_price"])
    wholesale_price = update_data.get("wholesale_price", existing_product["wholesale_price"])
    if wholesale_price >= retail_price:
        raise HTTPException(status_code=400, detail="Wholesale price must be less than retail price")
    
    # Handle backward compatibility for images
    if "images" in update_data and update_data["images"]:
        # Filter out empty strings
        update_data["images"] = [img for img in update_data["images"] if img.strip()]
        # Set first image as main image for backward compatibility  
        if update_data["images"]:
            update_data["image"] = update_data["images"][0]
    
    # Filter out empty strings from colors
    if "colors" in update_data and update_data["colors"]:
        update_data["colors"] = [color for color in update_data["colors"] if color.strip()]
    
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

@api_router.put("/products/{product_id}/stock/{size}")
async def update_stock(product_id: str, size: str, stock_update: StockUpdate, admin: Admin = Depends(get_current_admin)):
    """Update stock for a specific product size (admin only)"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update stock for the specific size
    update_query = {f"stock.{size}": stock_update.quantity, "updated_at": datetime.utcnow()}
    await db.products.update_one({"id": product_id}, {"$set": update_query})
    
    return {"message": f"Stock updated for size {size}"}

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
        {"id": "todos", "name": "Todos"},
        {"id": "vestidos", "name": "Vestidos"},
        {"id": "enterizos", "name": "Enterizos"},
        {"id": "conjuntos", "name": "Conjuntos"},
        {"id": "blusas", "name": "Blusas"},
        {"id": "faldas", "name": "Faldas"},
        {"id": "pantalones", "name": "Pantalones"}
    ]

# Catalog Analytics routes (admin only)
@api_router.get("/catalog/stats", response_model=CatalogStats)
async def get_catalog_stats(admin: Admin = Depends(get_current_admin)):
    """Get comprehensive catalog statistics"""
    
    # Get all products
    products = await db.products.find().to_list(length=None)
    
    # Basic stats
    total_products = len(products)
    
    # Products by category
    products_by_category = {}
    categories = ["vestidos", "enterizos", "conjuntos", "blusas", "faldas", "pantalones"]
    
    for category in categories:
        count = len([p for p in products if p.get("category") == category])
        products_by_category[category] = count
    
    # Calculate total stock values
    total_stock_value_retail = 0
    total_stock_value_wholesale = 0
    low_stock_products = []
    
    for product in products:
        stock = product.get("stock", {})
        total_stock = sum(stock.values())
        
        # Calculate stock values
        total_stock_value_retail += total_stock * product.get("retail_price", 0)
        total_stock_value_wholesale += total_stock * product.get("wholesale_price", 0)
        
        # Check for low stock (less than 5 total units)
        if total_stock < 5:
            low_stock_products.append(product.get("name", "Unknown"))
    
    return CatalogStats(
        total_products=total_products,
        products_by_category=products_by_category,
        total_stock_value_retail=total_stock_value_retail,
        total_stock_value_wholesale=total_stock_value_wholesale,
        low_stock_products=low_stock_products
    )

@api_router.get("/catalog/low-stock")
async def get_low_stock_products(admin: Admin = Depends(get_current_admin), threshold: int = 5):
    """Get products with low stock"""
    products = await db.products.find().to_list(length=None)
    
    low_stock_products = []
    for product in products:
        stock = product.get("stock", {})
        total_stock = sum(stock.values())
        
        if total_stock <= threshold:
            low_stock_products.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "total_stock": total_stock,
                "stock_by_size": stock
            })
    
    return low_stock_products

@api_router.get("/catalog/export")
async def export_catalog(admin: Admin = Depends(get_current_admin), format: str = "json"):
    """Export catalog data"""
    products = await db.products.find().to_list(length=None)
    
    # Remove internal MongoDB fields and convert to export format
    export_data = []
    for product in products:
        export_product = {
            "id": product.get("id"),
            "name": product.get("name"),
            "description": product.get("description"),
            "retail_price": product.get("retail_price"),
            "wholesale_price": product.get("wholesale_price"),
            "category": product.get("category"),
            "specifications": product.get("specifications"),
            "composition": product.get("composition"),
            "care": product.get("care"),
            "sizes": product.get("sizes", []),
            "stock": product.get("stock", {}),
            "total_stock": sum(product.get("stock", {}).values()),
            "created_at": product.get("created_at"),
            "updated_at": product.get("updated_at")
        }
        export_data.append(export_product)
    
    return {
        "format": format,
        "export_date": datetime.utcnow(),
        "total_products": len(export_data),
        "products": export_data
    }

@api_router.get("/catalog/search")
async def search_products(query: str, category: Optional[str] = None, limit: int = 50):
    """Search products by name or description"""
    search_filter = {
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"specifications": {"$regex": query, "$options": "i"}}
        ]
    }
    
    if category and category != "todos":
        search_filter["category"] = category
    
    products = await db.products.find(search_filter).limit(limit).to_list(limit)
    return [Product(**product) for product in products]

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
    logger.info("HANNU CLOTHES CATALOG API starting up...")
    
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
    
    # Create sample products if none exist
    product_count = await db.products.count_documents({})
    if product_count == 0:
        sample_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Vestido Rosa Elegante",
                "description": "Vestido elegante perfecto para ocasiones especiales. Confeccionado en tela de alta calidad con acabados refinados.",
                "retail_price": 150000,
                "wholesale_price": 105000,
                "category": "vestidos",
                "image": "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85",
                "specifications": "Vestido de corte A, manga corta, cuello redondo, cierre posterior invisible",
                "composition": "95% Algodón, 5% Elastano",
                "care": "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura media",
                "shipping_policy": "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
                "exchange_policy": "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
                "sizes": ["XS", "S", "M", "L", "XL"],
                "stock": {"XS": 5, "S": 8, "M": 12, "L": 10, "XL": 6},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for product in sample_products:
            await db.products.insert_one(product)
        
        logger.info(f"Created {len(sample_products)} sample products")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()