#!/usr/bin/env python3
"""
HANNU CLOTHES - Script de Restauración de Productos Eliminados
Restaura los productos que fueron eliminados incorrectamente
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
import uuid

# Cargar variables de entorno
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class ProductRestorer:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.restored_count = 0
        
    async def restore_deleted_products(self):
        """Restaura los productos eliminados incorrectamente"""
        print("🔄 RESTAURANDO PRODUCTOS ELIMINADOS INCORRECTAMENTE")
        print("=" * 60)
        
        # Productos que fueron eliminados pero que deberían existir
        products_to_restore = [
            {
                "id": str(uuid.uuid4()),
                "name": "Amelia",
                "description": "Elegante vestido Amelia con diseño sofisticado",
                "retail_price": 110000,
                "wholesale_price": 95000,
                "category": "vestidos",
                "images": [""],
                "colors": "",
                "sizes": "",
                "composition": "",
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Blonda",
                "description": "Vestido Blonda con detalles únicos",
                "retail_price": 110000,
                "wholesale_price": 95000,
                "category": "vestidos",
                "images": [""],
                "colors": "",
                "sizes": "",
                "composition": "",
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Sol",
                "description": "Enterizo Sol con diseño radiante",
                "retail_price": 100000,
                "wholesale_price": 85000,
                "category": "enterizos",
                "images": [""],
                "colors": "",
                "sizes": "",
                "composition": "",
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Jade",
                "description": "Conjunto Jade elegante",
                "retail_price": 60000,
                "wholesale_price": 45000,
                "category": "conjuntos",
                "images": [""],
                "colors": "",
                "sizes": "",
                "composition": "",
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Abigail",
                "description": "Vestido Abigail con estilo único",
                "retail_price": 75000,
                "wholesale_price": 52500,
                "category": "vestidos",
                "images": [""],
                "colors": "",
                "sizes": "",
                "composition": "",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
        ]
        
        for product in products_to_restore:
            try:
                # Verificar si ya existe un producto con este nombre exacto y categoría
                existing = await self.db.products.find_one({
                    "name": product["name"],
                    "category": product["category"]
                })
                
                if not existing:
                    await self.db.products.insert_one(product)
                    self.restored_count += 1
                    print(f"✅ Restaurado: {product['name']} ({product['category']}) - ${product['retail_price']:,}")
                else:
                    print(f"ℹ️ Ya existe: {product['name']} ({product['category']})")
                    
            except Exception as e:
                print(f"❌ Error restaurando {product['name']}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🎉 RESTAURACIÓN COMPLETADA")
        print("=" * 60)
        print(f"✅ Productos restaurados: {self.restored_count}")
        
        # Mostrar estadísticas finales
        total_products = await self.db.products.count_documents({})
        print(f"📦 Total productos en catálogo: {total_products}")
        
    async def run_restore(self):
        """Ejecuta la restauración"""
        await self.restore_deleted_products()
        self.client.close()

async def main():
    restorer = ProductRestorer()
    await restorer.run_restore()

if __name__ == "__main__":
    print("HANNU CLOTHES - Restaurador de Productos")
    print("Restaura productos eliminados incorrectamente")
    print()
    
    asyncio.run(main())