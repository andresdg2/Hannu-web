#!/usr/bin/env python3
"""
HANNU CLOTHES - Script de Limpieza de Productos Duplicados
Elimina productos duplicados manteniendo la versión más completa
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class DuplicateCleaner:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.deleted_count = 0
        
    async def find_duplicates(self):
        """Encuentra productos duplicados por nombre"""
        pipeline = [
            {"$group": {
                "_id": "$name",
                "count": {"$sum": 1},
                "products": {"$push": "$$ROOT"}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        
        duplicates = await self.db.products.aggregate(pipeline).to_list(None)
        return duplicates
    
    def choose_best_product(self, products):
        """Elige la mejor versión de un producto duplicado"""
        print(f"\n🔍 Analizando {len(products)} duplicados de '{products[0]['name']}':")
        
        best_product = None
        best_score = -1
        
        for i, product in enumerate(products):
            score = 0
            
            # Puntos por tener imágenes
            if product.get('images') and len([img for img in product['images'] if img]):
                score += len([img for img in product['images'] if img]) * 2
            
            # Puntos por tener imagen singular
            if product.get('image'):
                score += 1
                
            # Puntos por tener composición
            if product.get('composition'):
                score += 2
                
            # Puntos por tener colores
            if product.get('colors'):
                score += 1
                
            # Puntos por tener tallas
            if product.get('sizes'):
                score += 1
                
            # Puntos por precio mayorista válido
            if product.get('wholesale_price', 0) > 0:
                score += 3
            
            # Puntos por fecha más reciente (si existe)
            if product.get('created_at'):
                score += 1
            
            print(f"   Versión {i+1}: ${product.get('retail_price', 0):,} - Score: {score}")
            print(f"      Imágenes: {len(product.get('images', []))} | Mayorista: ${product.get('wholesale_price', 0):,}")
            
            if score > best_score:
                best_score = score
                best_product = product
        
        print(f"   ✅ Mejor versión: ${best_product.get('retail_price', 0):,} (Score: {best_score})")
        return best_product
    
    async def clean_duplicates(self):
        """Limpia productos duplicados manteniendo el mejor"""
        print("🧹 INICIANDO LIMPIEZA DE PRODUCTOS DUPLICADOS")
        print("=" * 60)
        
        duplicates = await self.find_duplicates()
        
        if not duplicates:
            print("✅ No se encontraron productos duplicados")
            return
        
        print(f"📦 Encontrados {len(duplicates)} grupos de productos duplicados")
        
        for duplicate_group in duplicates:
            name = duplicate_group['_id']
            products = duplicate_group['products']
            
            # Elegir el mejor producto
            best_product = self.choose_best_product(products)
            
            # Eliminar los otros productos
            for product in products:
                if product['id'] != best_product['id']:
                    try:
                        result = await self.db.products.delete_one({"id": product['id']})
                        if result.deleted_count > 0:
                            self.deleted_count += 1
                            print(f"   ❌ Eliminado duplicado: ${product.get('retail_price', 0):,}")
                    except Exception as e:
                        print(f"   ⚠️ Error eliminando {product['id']}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🎉 LIMPIEZA COMPLETADA")
        print("=" * 60)
        print(f"🗑️ Productos eliminados: {self.deleted_count}")
        print(f"✅ Duplicados resueltos: {len(duplicates)}")
        
        # Verificar resultado final
        final_duplicates = await self.find_duplicates()
        if not final_duplicates:
            print("✅ Todos los duplicados han sido eliminados correctamente")
        else:
            print(f"⚠️ Aún quedan {len(final_duplicates)} grupos duplicados")
    
    async def fix_aloruh_price(self):
        """Corrige el precio mayorista de Aloruh"""
        print("\n🔧 CORRIGIENDO PRECIO DE ALORUH")
        print("=" * 40)
        
        aloruh = await self.db.products.find_one({"name": {"$regex": "Aloruh", "$options": "i"}})
        
        if aloruh:
            if aloruh.get('wholesale_price', 0) == 0:
                retail_price = aloruh.get('retail_price', 0)
                # Calcular precio mayorista como 70% del retail
                new_wholesale_price = int(retail_price * 0.7)
                
                await self.db.products.update_one(
                    {"id": aloruh["id"]},
                    {"$set": {
                        "wholesale_price": new_wholesale_price,
                        "updated_at": datetime.utcnow()
                    }}
                )
                
                print(f"✅ Aloruh corregido: Retail ${retail_price:,} → Mayorista ${new_wholesale_price:,}")
            else:
                print(f"✅ Aloruh ya tiene precio mayorista válido: ${aloruh.get('wholesale_price', 0):,}")
        else:
            print("⚠️ Producto Aloruh no encontrado")
    
    async def run_cleanup(self):
        """Ejecuta la limpieza completa"""
        await self.clean_duplicates()
        await self.fix_aloruh_price()
        self.client.close()

async def main():
    cleaner = DuplicateCleaner()
    await cleaner.run_cleanup()

if __name__ == "__main__":
    print("HANNU CLOTHES - Limpiador de Productos Duplicados")
    print("Mantiene la mejor versión de cada producto duplicado")
    print()
    
    asyncio.run(main())