#!/usr/bin/env python3
"""
HANNU CLOTHES - Script de Migración Automática de Imágenes
Migra todas las imágenes de PostImg a ImgBB automáticamente
"""

import asyncio
import aiohttp
import base64
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import urlparse
import re
from datetime import datetime

# Configuración
IMGBB_API_KEY = "TU_API_KEY_AQUI"  # Reemplazar con tu API key de ImgBB
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'hannu_clothes')

class ImageMigrator:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.migrated_count = 0
        self.failed_count = 0
        self.total_count = 0
        
    async def get_all_products(self):
        """Obtiene todos los productos de la base de datos"""
        products = await self.db.products.find().to_list(length=None)
        print(f"📦 Encontrados {len(products)} productos en la base de datos")
        return products
    
    async def download_image(self, session, url):
        """Descarga una imagen desde PostImg"""
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.read()
                    if len(content) > 0:
                        return content
                    else:
                        print(f"   ❌ Imagen vacía: {url}")
                        return None
                else:
                    print(f"   ❌ Error HTTP {response.status}: {url}")
                    return None
        except Exception as e:
            print(f"   ❌ Error descargando {url}: {str(e)}")
            return None
    
    async def upload_to_imgbb(self, session, image_data, name):
        """Sube una imagen a ImgBB"""
        try:
            # Convertir a base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Preparar datos para ImgBB
            data = {
                'key': IMGBB_API_KEY,
                'image': image_base64,
                'name': name
            }
            
            async with session.post('https://api.imgbb.com/1/upload', data=data, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        new_url = result['data']['url']
                        print(f"   ✅ Subida exitosa: {new_url}")
                        return new_url
                    else:
                        print(f"   ❌ Error en respuesta de ImgBB: {result}")
                        return None
                else:
                    print(f"   ❌ Error HTTP ImgBB {response.status}")
                    return None
        except Exception as e:
            print(f"   ❌ Error subiendo a ImgBB: {str(e)}")
            return None
    
    def extract_image_name(self, url):
        """Extrae el nombre de la imagen desde la URL"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            # Generar nombre basado en la URL
            image_id = re.search(r'/([a-zA-Z0-9]+)/', parsed.path)
            if image_id:
                return f"hannu_{image_id.group(1)}"
            else:
                return f"hannu_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return filename.split('.')[0]  # Remover extensión
    
    async def migrate_image(self, session, url):
        """Migra una sola imagen de PostImg a ImgBB"""
        if not url or 'postimg.cc' not in url:
            return url  # No es una URL de PostImg, mantener original
        
        print(f"   🔄 Migrando: {url}")
        
        # Descargar imagen original
        image_data = await self.download_image(session, url)
        if not image_data:
            self.failed_count += 1
            return url  # Mantener URL original si falla
        
        # Extraer nombre de archivo
        image_name = self.extract_image_name(url)
        
        # Subir a ImgBB
        new_url = await self.upload_to_imgbb(session, image_data, image_name)
        if new_url:
            self.migrated_count += 1
            return new_url
        else:
            self.failed_count += 1
            return url  # Mantener URL original si falla
    
    async def migrate_product_images(self, session, product):
        """Migra todas las imágenes de un producto"""
        product_name = product.get('name', 'Unknown')
        print(f"\n📝 Procesando producto: {product_name}")
        
        updated = False
        
        # Migrar array de imágenes
        if product.get('images'):
            new_images = []
            for i, url in enumerate(product['images']):
                if url and 'postimg.cc' in url:
                    print(f"   Imagen {i+1}/{len(product['images'])}")
                    new_url = await self.migrate_image(session, url)
                    new_images.append(new_url)
                    if new_url != url:
                        updated = True
                else:
                    new_images.append(url)
            
            if updated:
                product['images'] = new_images
        
        # Migrar imagen singular (compatibilidad)
        if product.get('image') and 'postimg.cc' in product['image']:
            print(f"   Imagen singular")
            new_url = await self.migrate_image(session, product['image'])
            if new_url != product['image']:
                product['image'] = new_url
                updated = True
        
        return updated, product
    
    async def update_product_in_db(self, product):
        """Actualiza un producto en la base de datos"""
        try:
            result = await self.db.products.update_one(
                {"id": product["id"]},
                {"$set": {
                    "images": product.get("images", []),
                    "image": product.get("image", ""),
                    "updated_at": datetime.utcnow()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"   ❌ Error actualizando producto en BD: {str(e)}")
            return False
    
    async def run_migration(self):
        """Ejecuta la migración completa"""
        if IMGBB_API_KEY == "TU_API_KEY_AQUI":
            print("❌ ERROR: Debes configurar tu IMGBB_API_KEY en el script")
            return
        
        print("🚀 INICIANDO MIGRACIÓN AUTOMÁTICA DE IMÁGENES")
        print("=" * 60)
        
        # Obtener todos los productos
        products = await self.get_all_products()
        if not products:
            print("❌ No se encontraron productos")
            return
        
        # Contar imágenes de PostImg
        postimg_images = 0
        for product in products:
            if product.get('images'):
                postimg_images += sum(1 for img in product['images'] if img and 'postimg.cc' in img)
            if product.get('image') and 'postimg.cc' in product['image']:
                postimg_images += 1
        
        self.total_count = postimg_images
        print(f"📊 Imágenes de PostImg encontradas: {postimg_images}")
        
        if postimg_images == 0:
            print("✅ No hay imágenes de PostImg para migrar")
            return
        
        # Crear sesión HTTP
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Procesar cada producto
            products_updated = 0
            for i, product in enumerate(products, 1):
                print(f"\n--- Producto {i}/{len(products)} ---")
                
                updated, updated_product = await self.migrate_product_images(session, product)
                
                if updated:
                    success = await self.update_product_in_db(updated_product)
                    if success:
                        products_updated += 1
                        print(f"   ✅ Producto actualizado en BD")
                    else:
                        print(f"   ❌ Error actualizando producto en BD")
                else:
                    print(f"   ℹ️  Sin imágenes de PostImg para migrar")
                
                # Progreso cada 10 productos
                if i % 10 == 0:
                    print(f"\n📊 PROGRESO: {i}/{len(products)} productos procesados")
                    print(f"   ✅ Migradas: {self.migrated_count}")
                    print(f"   ❌ Fallidas: {self.failed_count}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("🎉 MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print(f"📦 Productos procesados: {len(products)}")
        print(f"📝 Productos actualizados: {products_updated}")
        print(f"🖼️  Total imágenes encontradas: {self.total_count}")
        print(f"✅ Imágenes migradas exitosamente: {self.migrated_count}")
        print(f"❌ Imágenes que fallaron: {self.failed_count}")
        
        if self.migrated_count > 0:
            print(f"\n🎊 ¡ÉXITO! {self.migrated_count} imágenes migradas a ImgBB")
            print("🚀 Tu catálogo ahora usa imágenes compatibles con CORS")
        
        # Cerrar conexión a MongoDB
        self.client.close()

async def main():
    migrator = ImageMigrator()
    await migrator.run_migration()

if __name__ == "__main__":
    print("HANNU CLOTHES - Migrador Automático de Imágenes")
    print("Migra de PostImg a ImgBB para solucionar problemas de CORS")
    print()
    
    # Verificar que tenemos la API key
    if len(sys.argv) > 1:
        global IMGBB_API_KEY
        IMGBB_API_KEY = sys.argv[1]
    
    asyncio.run(main())