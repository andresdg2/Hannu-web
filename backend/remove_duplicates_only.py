#!/usr/bin/env python3
"""
HANNU CLOTHES - Script para eliminar solo duplicados exactos
Elimina duplicados de Jade y Sol dejando solo uno de cada uno
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

class SimpleDuplicateRemover:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.removed_count = 0
        
    async def remove_specific_duplicates(self):
        """Elimina duplicados específicos de Jade y Sol"""
        print("🔧 ELIMINANDO DUPLICADOS ESPECÍFICOS - JADE Y SOL")
        print("=" * 50)
        
        # Buscar productos Jade
        jade_products = await self.db.products.find({"name": {"$regex": "^Jade$", "$options": "i"}}).to_list(None)
        print(f"Encontrados {len(jade_products)} productos 'Jade'")
        
        if len(jade_products) > 1:
            # Mantener el primero, eliminar los demás
            for i, product in enumerate(jade_products[1:], 1):
                try:
                    await self.db.products.delete_one({"id": product["id"]})
                    self.removed_count += 1
                    print(f"   ❌ Eliminado Jade duplicado {i}: ${product.get('retail_price', 0):,} ({product.get('category', 'sin categoría')})")
                except Exception as e:
                    print(f"   ⚠️ Error eliminando Jade {i}: {str(e)}")
        
        # Buscar productos Sol
        sol_products = await self.db.products.find({"name": {"$regex": "^Sol$", "$options": "i"}}).to_list(None)
        print(f"\nEncontrados {len(sol_products)} productos 'Sol'")
        
        if len(sol_products) > 1:
            # Mantener el primero, eliminar los demás
            for i, product in enumerate(sol_products[1:], 1):
                try:
                    await self.db.products.delete_one({"id": product["id"]})
                    self.removed_count += 1
                    print(f"   ❌ Eliminado Sol duplicado {i}: ${product.get('retail_price', 0):,} ({product.get('category', 'sin categoría')})")
                except Exception as e:
                    print(f"   ⚠️ Error eliminando Sol {i}: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✅ ELIMINACIÓN COMPLETADA")
        print("=" * 50)
        print(f"🗑️ Duplicados eliminados: {self.removed_count}")
        
        # Verificar resultado
        final_jade = await self.db.products.count_documents({"name": {"$regex": "^Jade$", "$options": "i"}})
        final_sol = await self.db.products.count_documents({"name": {"$regex": "^Sol$", "$options": "i"}})
        
        print(f"📦 Jade restantes: {final_jade}")
        print(f"📦 Sol restantes: {final_sol}")
        
        if final_jade == 1 and final_sol == 1:
            print("🎉 Perfecto: Solo queda 1 Jade y 1 Sol para editar manualmente")
        else:
            print("⚠️ Revisar: Aún pueden quedar duplicados")
    
    async def run_removal(self):
        """Ejecuta la eliminación"""
        await self.remove_specific_duplicates()
        self.client.close()

async def main():
    remover = SimpleDuplicateRemover()
    await remover.run_removal()

if __name__ == "__main__":
    print("HANNU CLOTHES - Eliminador de Duplicados Específicos")
    print("Elimina duplicados de Jade y Sol para edición manual")
    print()
    
    asyncio.run(main())