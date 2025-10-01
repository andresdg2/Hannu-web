#!/usr/bin/env python3
"""
URGENT INVESTIGATION: Mass Upload Completion Analysis
Investigates the current state after mass upload completion
"""

import requests
import json
from datetime import datetime, timedelta

class MassUploadInvestigator:
    def __init__(self):
        self.base_url = "https://fashion-admin-4.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        
    def login_admin(self):
        """Login as admin to get token"""
        try:
            response = requests.post(
                f"{self.api_url}/admin/login",
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                print("✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_all_products(self):
        """Get all products from database"""
        try:
            response = requests.get(
                f"{self.api_url}/products?limit=1000",
                timeout=10
            )
            if response.status_code == 200:
                products = response.json()
                print(f"✅ Retrieved {len(products)} products from database")
                return products
            else:
                print(f"❌ Failed to get products: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting products: {str(e)}")
            return []
    
    def analyze_image_status(self, products):
        """Analyze current image status of all products"""
        print("\n🔍 ANALYZING IMAGE STATUS:")
        print("="*60)
        
        stats = {
            'total_products': len(products),
            'with_imgbb': 0,
            'with_postimg_only': 0,
            'with_mixed': 0,
            'without_images': 0,
            'recently_updated': 0
        }
        
        imgbb_products = []
        postimg_only_products = []
        mixed_products = []
        no_image_products = []
        recently_updated_products = []
        
        # Calculate yesterday's date for recent updates
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        
        for product in products:
            name = product.get('name', 'Unknown')
            category = product.get('category', 'unknown')
            
            # Check if recently updated
            updated_at = product.get('updated_at')
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).date()
                        if update_date >= yesterday:
                            recently_updated_products.append(product)
                            stats['recently_updated'] += 1
                except:
                    pass
            
            # Analyze images
            images = product.get('images', [])
            single_image = product.get('image', '')
            
            # Combine all image URLs
            all_images = list(images) if images else []
            if single_image and single_image not in all_images:
                all_images.append(single_image)
            
            if not all_images:
                no_image_products.append({'name': name, 'category': category})
                stats['without_images'] += 1
                continue
            
            # Check image types
            has_imgbb = any('ibb.co' in img for img in all_images)
            has_postimg = any('postimg' in img for img in all_images)
            
            if has_imgbb and has_postimg:
                mixed_products.append({
                    'name': name, 
                    'category': category, 
                    'images': all_images
                })
                stats['with_mixed'] += 1
            elif has_imgbb:
                imgbb_products.append({
                    'name': name, 
                    'category': category, 
                    'images': all_images
                })
                stats['with_imgbb'] += 1
            elif has_postimg:
                postimg_only_products.append({
                    'name': name, 
                    'category': category, 
                    'images': all_images
                })
                stats['with_postimg_only'] += 1
        
        # Print statistics
        print(f"📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Total productos: {stats['total_products']}")
        print(f"   • Con imágenes ImgBB: {stats['with_imgbb']}")
        print(f"   • Solo PostImg: {stats['with_postimg_only']}")
        print(f"   • Mixto (ImgBB + PostImg): {stats['with_mixed']}")
        print(f"   • Sin imágenes: {stats['without_images']}")
        print(f"   • Actualizados recientemente: {stats['recently_updated']}")
        
        # Calculate success rate
        working_images = stats['with_imgbb'] + stats['with_mixed']
        success_rate = (working_images / stats['total_products']) * 100
        print(f"\n📈 TASA DE ÉXITO ACTUAL: {success_rate:.1f}%")
        
        return {
            'stats': stats,
            'imgbb_products': imgbb_products,
            'postimg_only_products': postimg_only_products,
            'mixed_products': mixed_products,
            'no_image_products': no_image_products,
            'recently_updated_products': recently_updated_products
        }
    
    def identify_products_needing_images(self, analysis):
        """Identify specific products that still need images"""
        print("\n🚨 PRODUCTOS QUE AÚN NECESITAN IMÁGENES:")
        print("="*60)
        
        # Products with only PostImg (likely broken)
        postimg_products = analysis['postimg_only_products']
        
        # Test a sample of PostImg URLs to confirm they're broken
        broken_postimg_products = []
        
        print(f"🔍 Verificando {min(10, len(postimg_products))} productos con PostImg...")
        
        for i, product in enumerate(postimg_products[:10]):
            name = product['name']
            images = product['images']
            working_images = 0
            
            for img_url in images:
                if 'postimg' in img_url:
                    try:
                        response = requests.head(img_url, timeout=3)
                        if response.status_code == 200:
                            working_images += 1
                            print(f"   ✅ {name}: Imagen funciona")
                            break
                    except:
                        pass
            
            if working_images == 0:
                broken_postimg_products.append(product)
                print(f"   ❌ {name}: Todas las imágenes PostImg rotas")
        
        # Combine products needing images
        products_needing_images = analysis['no_image_products'] + broken_postimg_products
        
        # Group by category
        by_category = {}
        for product in products_needing_images:
            category = product['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(product)
        
        print(f"\n📋 RESUMEN POR CATEGORÍA:")
        total_needing_images = 0
        for category, products_list in by_category.items():
            print(f"\n   📂 {category.upper()} ({len(products_list)} productos):")
            total_needing_images += len(products_list)
            for j, product in enumerate(products_list[:5]):
                print(f"      {j+1}. {product['name']}")
            if len(products_list) > 5:
                print(f"      ... y {len(products_list) - 5} más")
        
        print(f"\n🎯 TOTAL PRODUCTOS NECESITANDO IMÁGENES: {total_needing_images}")
        
        return products_needing_images, by_category
    
    def test_upload_endpoint(self):
        """Test if the mass upload endpoint is working"""
        print("\n🔧 VERIFICANDO ENDPOINT DE CARGA MASIVA:")
        print("="*60)
        
        if not self.token:
            print("❌ No hay token de admin")
            return False
        
        try:
            # Test endpoint availability (expect 400 because no files sent)
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{self.api_url}/admin/upload-images",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 400:
                print("✅ Endpoint /api/admin/upload-images está disponible")
                return True
            else:
                print(f"⚠️  Endpoint responde con código: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error probando endpoint: {str(e)}")
            return False
    
    def generate_action_plan(self, products_needing_images, by_category):
        """Generate specific action plan to reach 100%"""
        print("\n📋 PLAN DE ACCIÓN PARA LLEGAR AL 100%:")
        print("="*60)
        
        total_needing = len(products_needing_images)
        
        print(f"🎯 OBJETIVO: Re-subir imágenes para {total_needing} productos")
        print(f"\n📝 PRODUCTOS ESPECÍFICOS POR PRIORIDAD:")
        
        # Prioritize by category size
        sorted_categories = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (category, products_list) in enumerate(sorted_categories):
            print(f"\n   {i+1}. CATEGORÍA: {category.upper()} - {len(products_list)} productos")
            for j, product in enumerate(products_list):
                print(f"      • {product['name']}")
        
        print(f"\n🔧 PASOS RECOMENDADOS:")
        print(f"   1. Preparar imágenes para los {total_needing} productos listados arriba")
        print(f"   2. Usar endpoint /api/admin/upload-images para carga masiva")
        print(f"   3. Verificar que todas las nuevas URLs sean de ImgBB")
        print(f"   4. Confirmar que las imágenes carguen correctamente en el frontend")
        
        return sorted_categories
    
    def run_investigation(self):
        """Run complete investigation"""
        print("🚨 INVESTIGACIÓN URGENTE - CARGA MASIVA INCOMPLETA")
        print("="*80)
        print("OBJETIVO: Verificar exactamente qué productos aún necesitan imágenes")
        print("="*80)
        
        # Step 1: Login
        if not self.login_admin():
            return
        
        # Step 2: Get all products
        products = self.get_all_products()
        if not products:
            return
        
        # Step 3: Analyze image status
        analysis = self.analyze_image_status(products)
        
        # Step 4: Identify products needing images
        products_needing_images, by_category = self.identify_products_needing_images(analysis)
        
        # Step 5: Test upload endpoint
        self.test_upload_endpoint()
        
        # Step 6: Generate action plan
        self.generate_action_plan(products_needing_images, by_category)
        
        print("\n" + "="*80)
        print("✅ INVESTIGACIÓN COMPLETADA")
        print("="*80)

if __name__ == "__main__":
    investigator = MassUploadInvestigator()
    investigator.run_investigation()