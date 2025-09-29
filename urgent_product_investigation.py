import requests
import sys
import json
from datetime import datetime, timedelta

class UrgentProductInvestigation:
    def __init__(self, base_url="https://fashion-admin-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.investigation_results = {}

    def authenticate(self):
        """Get admin token for authenticated requests"""
        print("🔐 Authenticating admin user...")
        try:
            response = requests.post(
                f"{self.api_url}/admin/login",
                json={"username": self.admin_username, "password": self.admin_password},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def get_headers(self):
        """Get headers with authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def investigate_existing_products(self):
        """INVESTIGACIÓN 1: Productos existentes"""
        print("\n" + "="*60)
        print("🔍 INVESTIGACIÓN 1: PRODUCTOS EXISTENTES")
        print("="*60)
        
        # Count ALL products in database
        print("\n📊 Contando TODOS los productos en la base de datos...")
        try:
            # Try with high limit to get all products
            response = requests.get(
                f"{self.api_url}/products?limit=1000",
                headers=self.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                products = response.json()
                total_count = len(products)
                print(f"✅ TOTAL DE PRODUCTOS ENCONTRADOS: {total_count}")
                self.investigation_results['total_products'] = total_count
                
                if total_count == 0:
                    print("❌ CRÍTICO: NO HAY PRODUCTOS EN LA BASE DE DATOS")
                    return products
                
                # List first 10 products by creation date (oldest first)
                print(f"\n📋 Listando los primeros 10 productos por fecha de creación (más antiguos primero):")
                
                # Sort by created_at (oldest first)
                products_with_dates = []
                for product in products:
                    created_at = product.get('created_at')
                    if created_at:
                        try:
                            # Parse the datetime string
                            if isinstance(created_at, str):
                                # Handle different datetime formats
                                if 'T' in created_at:
                                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                else:
                                    dt = datetime.fromisoformat(created_at)
                            else:
                                dt = created_at
                            products_with_dates.append((product, dt))
                        except:
                            # If parsing fails, use current time
                            products_with_dates.append((product, datetime.now()))
                    else:
                        # If no created_at, use current time
                        products_with_dates.append((product, datetime.now()))
                
                # Sort by date (oldest first)
                products_with_dates.sort(key=lambda x: x[1])
                
                print(f"   {'#':<3} {'Nombre':<30} {'Categoría':<12} {'Fecha Creación':<20}")
                print(f"   {'-'*3} {'-'*30} {'-'*12} {'-'*20}")
                
                for i, (product, dt) in enumerate(products_with_dates[:10]):
                    name = product.get('name', 'Sin nombre')[:28]
                    category = product.get('category', 'Sin cat')[:10]
                    date_str = dt.strftime('%Y-%m-%d %H:%M') if dt else 'Sin fecha'
                    print(f"   {i+1:<3} {name:<30} {category:<12} {date_str:<20}")
                
                # Check for products with dates before today
                today = datetime.now().date()
                products_before_today = []
                
                for product, dt in products_with_dates:
                    if dt.date() < today:
                        products_before_today.append((product, dt))
                
                print(f"\n📅 Productos con fechas anteriores a hoy ({today}):")
                print(f"   ENCONTRADOS: {len(products_before_today)} productos")
                
                if len(products_before_today) > 0:
                    print(f"   Ejemplos de productos antiguos:")
                    for i, (product, dt) in enumerate(products_before_today[:5]):
                        name = product.get('name', 'Sin nombre')[:25]
                        date_str = dt.strftime('%Y-%m-%d')
                        print(f"   • {name} (creado: {date_str})")
                
                # Check for specific product names mentioned by user
                print(f"\n🔍 Buscando productos específicos mencionados por el usuario:")
                search_terms = ['vestido', 'blusa', 'enterizo', 'conjunto', 'falda', 'pantalón']
                
                for term in search_terms:
                    matching_products = [p for p in products if term.lower() in p.get('name', '').lower() or term.lower() in p.get('category', '').lower()]
                    print(f"   • Productos con '{term}': {len(matching_products)}")
                    
                    if len(matching_products) > 0:
                        for product in matching_products[:3]:  # Show first 3 examples
                            print(f"     - {product.get('name', 'Sin nombre')}")
                
                return products
                
            else:
                print(f"❌ Error al obtener productos: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error en investigación de productos: {str(e)}")
            return []

    def investigate_deletion_problem(self, products):
        """INVESTIGACIÓN 2: Problema de eliminación"""
        print("\n" + "="*60)
        print("🗑️ INVESTIGACIÓN 2: PROBLEMA DE ELIMINACIÓN")
        print("="*60)
        
        if not products or len(products) == 0:
            print("❌ No hay productos para probar eliminación")
            return False
        
        # Create a test product first
        print("\n🧪 Creando producto de prueba para probar eliminación...")
        test_product = {
            "name": "PRODUCTO PRUEBA ELIMINACIÓN",
            "description": "Producto temporal para probar funcionalidad de eliminación",
            "retail_price": 50000,
            "wholesale_price": 35000,
            "category": "vestidos",
            "images": ["https://example.com/test.jpg"],
            "colors": ["Rojo"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/products",
                json=test_product,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                created_product = response.json()
                product_id = created_product.get('id')
                print(f"✅ Producto de prueba creado con ID: {product_id}")
                
                # Now try to delete it
                print(f"\n🗑️ Probando DELETE /api/products/{product_id} con token admin...")
                
                delete_response = requests.delete(
                    f"{self.api_url}/products/{product_id}",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if delete_response.status_code == 200:
                    print(f"✅ Eliminación exitosa: {delete_response.json()}")
                    
                    # Verify product was actually deleted
                    verify_response = requests.get(
                        f"{self.api_url}/products/{product_id}",
                        headers=self.get_headers(),
                        timeout=10
                    )
                    
                    if verify_response.status_code == 404:
                        print(f"✅ Verificación: Producto efectivamente eliminado de la base de datos")
                        return True
                    else:
                        print(f"❌ PROBLEMA: Producto aún existe después de eliminación")
                        return False
                        
                else:
                    print(f"❌ Error en eliminación: {delete_response.status_code} - {delete_response.text}")
                    return False
                    
            else:
                print(f"❌ No se pudo crear producto de prueba: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba de eliminación: {str(e)}")
            return False

    def investigate_edit_problem(self, products):
        """INVESTIGACIÓN 3: Problema de edición"""
        print("\n" + "="*60)
        print("✏️ INVESTIGACIÓN 3: PROBLEMA DE EDICIÓN")
        print("="*60)
        
        if not products or len(products) == 0:
            print("❌ No hay productos para probar edición")
            return False
        
        # Create a test product first
        print("\n🧪 Creando producto de prueba para probar edición...")
        test_product = {
            "name": "PRODUCTO PRUEBA EDICIÓN",
            "description": "Producto temporal para probar funcionalidad de edición",
            "retail_price": 60000,
            "wholesale_price": 42000,
            "category": "blusas",
            "images": ["https://example.com/original.jpg", "https://example.com/original2.jpg"],
            "colors": ["Azul", "Verde"],
            "composition": "100% Algodón",
            "sizes": ["S", "M", "L"]
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/products",
                json=test_product,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                created_product = response.json()
                product_id = created_product.get('id')
                print(f"✅ Producto de prueba creado con ID: {product_id}")
                
                # Now try to edit it with comprehensive updates
                print(f"\n✏️ Probando PUT /api/products/{product_id} con actualización completa...")
                
                update_data = {
                    "name": "PRODUCTO EDITADO - ACTUALIZADO",
                    "description": "Descripción actualizada después de edición",
                    "retail_price": 75000,
                    "wholesale_price": 52500,
                    "images": ["https://example.com/updated1.jpg", "https://example.com/updated2.jpg", "https://example.com/updated3.jpg"],
                    "colors": ["Rojo", "Negro", "Blanco"],
                    "composition": "95% Algodón, 5% Elastano",
                    "sizes": ["XS", "S", "M", "L", "XL"]
                }
                
                edit_response = requests.put(
                    f"{self.api_url}/products/{product_id}",
                    json=update_data,
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if edit_response.status_code == 200:
                    updated_product = edit_response.json()
                    print(f"✅ Edición exitosa")
                    
                    # Verify all fields were updated correctly
                    print(f"\n🔍 Verificando que todos los campos se mantuvieron:")
                    
                    checks = [
                        ("Nombre", updated_product.get('name'), update_data['name']),
                        ("Descripción", updated_product.get('description'), update_data['description']),
                        ("Precio retail", updated_product.get('retail_price'), update_data['retail_price']),
                        ("Precio mayorista", updated_product.get('wholesale_price'), update_data['wholesale_price']),
                        ("Imágenes", updated_product.get('images'), update_data['images']),
                        ("Colores", updated_product.get('colors'), update_data['colors']),
                        ("Composición", updated_product.get('composition'), update_data['composition']),
                        ("Tallas", updated_product.get('sizes'), update_data['sizes'])
                    ]
                    
                    all_correct = True
                    for field_name, actual, expected in checks:
                        if actual == expected:
                            print(f"   ✅ {field_name}: Correcto")
                        else:
                            print(f"   ❌ {field_name}: Esperado {expected}, obtenido {actual}")
                            all_correct = False
                    
                    # Clean up test product
                    requests.delete(f"{self.api_url}/products/{product_id}", headers=self.get_headers())
                    
                    return all_correct
                    
                else:
                    print(f"❌ Error en edición: {edit_response.status_code} - {edit_response.text}")
                    # Clean up test product
                    requests.delete(f"{self.api_url}/products/{product_id}", headers=self.get_headers())
                    return False
                    
            else:
                print(f"❌ No se pudo crear producto de prueba: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba de edición: {str(e)}")
            return False

    def investigate_database_verification(self):
        """INVESTIGACIÓN 4: Verificación de base de datos"""
        print("\n" + "="*60)
        print("🗄️ INVESTIGACIÓN 4: VERIFICACIÓN DE BASE DE DATOS")
        print("="*60)
        
        # Test with different limits and parameters
        print("\n🔍 Probando GET /api/products con diferentes parámetros...")
        
        test_cases = [
            ("Límite 1000", "products?limit=1000"),
            ("Sin límite", "products"),
            ("Categoría vestidos", "products?category=vestidos"),
            ("Categoría blusas", "products?category=blusas"),
            ("Categoría enterizos", "products?category=enterizos"),
            ("Categoría conjuntos", "products?category=conjuntos"),
            ("Búsqueda 'vestido'", "catalog/search?query=vestido"),
            ("Búsqueda 'blusa'", "catalog/search?query=blusa")
        ]
        
        results = {}
        
        for test_name, endpoint in test_cases:
            try:
                response = requests.get(
                    f"{self.api_url}/{endpoint}",
                    headers=self.get_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    results[test_name] = count
                    print(f"   ✅ {test_name}: {count} productos")
                    
                    # Show sample product names if any found
                    if count > 0 and isinstance(data, list):
                        sample_names = [p.get('name', 'Sin nombre') for p in data[:3]]
                        print(f"      Ejemplos: {', '.join(sample_names)}")
                        
                else:
                    results[test_name] = f"Error {response.status_code}"
                    print(f"   ❌ {test_name}: Error {response.status_code}")
                    
            except Exception as e:
                results[test_name] = f"Error: {str(e)}"
                print(f"   ❌ {test_name}: Error {str(e)}")
        
        # Check for products with different states or hidden products
        print(f"\n🔍 Verificando productos con diferentes estados...")
        
        try:
            # Get catalog stats for comprehensive view
            stats_response = requests.get(
                f"{self.api_url}/catalog/stats",
                headers=self.get_headers(),
                timeout=10
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"   📊 Estadísticas del catálogo:")
                print(f"      Total productos: {stats.get('total_products', 0)}")
                print(f"      Por categoría: {stats.get('products_by_category', {})}")
                print(f"      Productos con poco stock: {len(stats.get('low_stock_products', []))}")
                
                self.investigation_results['catalog_stats'] = stats
                
            else:
                print(f"   ❌ No se pudieron obtener estadísticas: {stats_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error obteniendo estadísticas: {str(e)}")
        
        return results

    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        print("\n" + "="*80)
        print("📋 REPORTE FINAL DE INVESTIGACIÓN URGENTE")
        print("="*80)
        
        print(f"\n🕐 Fecha y hora de investigación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL investigada: {self.base_url}")
        print(f"👤 Credenciales utilizadas: {self.admin_username}/admin123")
        
        # Summary of findings
        total_products = self.investigation_results.get('total_products', 0)
        
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"   • Total de productos encontrados: {total_products}")
        
        if total_products == 0:
            print(f"   ❌ CRÍTICO: NO SE ENCONTRARON PRODUCTOS EN LA BASE DE DATOS")
            print(f"   ❌ ESTO CONFIRMA QUE LOS 300+ PRODUCTOS REPORTADOS HAN DESAPARECIDO")
        elif total_products < 50:
            print(f"   ⚠️  PROBLEMA CONFIRMADO: Solo {total_products} productos encontrados")
            print(f"   ⚠️  Esto es significativamente menor a los 300+ reportados por el usuario")
        else:
            print(f"   ✅ Se encontraron {total_products} productos en la base de datos")
        
        # Recommendations
        print(f"\n🎯 RECOMENDACIONES URGENTES:")
        
        if total_products == 0:
            print(f"   1. ❌ CRÍTICO: Verificar respaldo de base de datos inmediatamente")
            print(f"   2. ❌ CRÍTICO: Revisar logs del servidor para identificar cuándo se perdieron los datos")
            print(f"   3. ❌ CRÍTICO: Contactar al administrador de base de datos")
            print(f"   4. ❌ CRÍTICO: Implementar recuperación de datos desde respaldo más reciente")
        elif total_products < 100:
            print(f"   1. ⚠️  Verificar si hay filtros o límites ocultos en las consultas")
            print(f"   2. ⚠️  Revisar logs de eliminación masiva de productos")
            print(f"   3. ⚠️  Verificar integridad de la base de datos")
            print(f"   4. ⚠️  Considerar recuperación parcial desde respaldo")
        else:
            print(f"   1. ✅ Verificar con el usuario si está viendo la vista correcta del catálogo")
            print(f"   2. ✅ Revisar filtros de frontend que puedan estar ocultando productos")
            print(f"   3. ✅ Verificar paginación y límites en la interfaz de usuario")
        
        print(f"\n🚨 ESTADO CRÍTICO DEL SISTEMA:")
        if total_products == 0:
            print(f"   🔴 ROJO - Sistema no funcional, pérdida total de datos")
        elif total_products < 50:
            print(f"   🟡 AMARILLO - Sistema parcialmente funcional, pérdida significativa de datos")
        else:
            print(f"   🟢 VERDE - Sistema funcional, posible problema de visualización")

def main():
    print("🚨 INVESTIGACIÓN URGENTE - PRODUCTOS PERDIDOS")
    print("="*80)
    print("Usuario reporta que 300+ productos originales han desaparecido del catálogo")
    print("Iniciando investigación exhaustiva...")
    
    investigator = UrgentProductInvestigation()
    
    # Authenticate first
    if not investigator.authenticate():
        print("❌ CRÍTICO: No se pudo autenticar. Investigación abortada.")
        return 1
    
    # Run investigations
    print("\n🔍 Ejecutando 4 investigaciones críticas...")
    
    # Investigation 1: Existing products
    products = investigator.investigate_existing_products()
    
    # Investigation 2: Deletion problem
    investigator.investigate_deletion_problem(products)
    
    # Investigation 3: Edit problem  
    investigator.investigate_edit_problem(products)
    
    # Investigation 4: Database verification
    investigator.investigate_database_verification()
    
    # Generate final report
    investigator.generate_investigation_report()
    
    print(f"\n✅ Investigación completada. Revisar reporte detallado arriba.")
    return 0

if __name__ == "__main__":
    sys.exit(main())