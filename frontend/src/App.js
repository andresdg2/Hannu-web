import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { ShoppingCart, User, Search, Menu, X, Heart, Star, ArrowRight, Check, Phone, Mail, MapPin, Plus, Edit, Trash2, Upload, Save, Eye, MessageCircle, Instagram, Facebook } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sample product data with dual pricing
const sampleProducts = [
  {
    id: 1,
    name: "Vestido Rosa Elegante",
    description: "Vestido elegante perfecto para ocasiones especiales. Confeccionado en tela de alta calidad con acabados refinados.",
    retail_price: 150000,
    wholesale_price: 105000,
    category: "vestidos",
    image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85",
    specifications: "Vestido de corte A, manga corta, cuello redondo, cierre posterior invisible",
    composition: "95% Algodón, 5% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura media",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["XS", "S", "M", "L", "XL"],
    stock: {"XS": 5, "S": 8, "M": 12, "L": 10, "XL": 6}
  },
  {
    id: 2,
    name: "Blusa Rayas Esencial",
    description: "Blusa de rayas clásica que combina con todo. Ideal para el día a día con un toque elegante y versátil.",
    retail_price: 75000,
    wholesale_price: 52500,
    category: "blusas",
    image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85",
    specifications: "Blusa de rayas horizontales, manga larga, cuello camisero, botones frontales",
    composition: "100% Algodón orgánico",
    care: "Lavar a máquina en agua tibia, secar al aire, planchar del revés",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["XS", "S", "M", "L", "XL"],
    stock: {"XS": 3, "S": 6, "M": 8, "L": 7, "XL": 4}
  },
  {
    id: 3,
    name: "Pantalón Denim Premium",
    description: "Pantalón de mezclilla de corte perfecto con acabado premium. Comodidad y estilo en una sola prenda.",
    retail_price: 120000,
    wholesale_price: 84000,
    category: "pantalones",
    image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85",
    specifications: "Pantalón de mezclilla, corte recto, tiro medio, cinco bolsillos",
    composition: "82% Algodón, 16% Poliéster, 2% Elastano",
    care: "Lavar del revés en agua fría, no usar blanqueador, secar colgado",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["26", "28", "30", "32", "34", "36"],
    stock: {"26": 4, "28": 7, "30": 9, "32": 8, "34": 6, "36": 3}
  },
  {
    id: 4,
    name: "Enterizo Elegante",
    description: "Enterizo sofisticado perfecto para eventos especiales. Diseño moderno con corte favorecedor.",
    retail_price: 185000,
    wholesale_price: 129500,
    category: "enterizos",
    image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85",
    specifications: "Enterizo de pierna ancha, tirantes ajustables, cintura marcada, bolsillos laterales",
    composition: "88% Poliéster, 12% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura baja",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["XS", "S", "M", "L", "XL"],
    stock: {"XS": 2, "S": 5, "M": 7, "L": 6, "XL": 3}
  },
  {
    id: 5,
    name: "Falda Midi Clásica",
    description: "Falda midi de corte clásico, perfecta para looks profesionales y casuales elegantes.",
    retail_price: 95000,
    wholesale_price: 66500,
    category: "faldas",
    image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85",
    specifications: "Falda midi, corte A, pretina alta, cierre lateral invisible",
    composition: "90% Poliéster, 10% Elastano",
    care: "Lavar a máquina en agua fría, secar colgado, planchar a temperatura media",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["XS", "S", "M", "L", "XL"],
    stock: {"XS": 6, "S": 8, "M": 10, "L": 7, "XL": 4}
  },
  {
    id: 6,
    name: "Conjunto Coordinado",
    description: "Conjunto de dos piezas coordinadas, perfecto para un look completo y sofisticado.",
    retail_price: 220000,
    wholesale_price: 154000,
    category: "conjuntos",
    image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85",
    specifications: "Conjunto de blusa y pantalón a juego, blusa con manga 3/4, pantalón de tiro alto",
    composition: "85% Viscosa, 15% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura baja",
    shipping_policy: "Envío nacional 2-5 días hábiles. Envío gratis en compras superiores a $200.000",
    exchange_policy: "Cambios y devoluciones hasta 15 días después de la compra. El producto debe estar en perfectas condiciones.",
    sizes: ["XS", "S", "M", "L", "XL"],
    stock: {"XS": 3, "S": 5, "M": 8, "L": 6, "XL": 2}
  }
];

const categories = [
  { id: "todos", name: "Todos", image: null },
  { id: "vestidos", name: "Vestidos", image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85" },
  { id: "enterizos", name: "Enterizos", image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85" },
  { id: "conjuntos", name: "Conjuntos", image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85" },
  { id: "blusas", name: "Blusas", image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85" },
  { id: "faldas", name: "Faldas & Pantalones", image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85" }
];

const Header = ({ selectedCategory, setSelectedCategory, showAdmin, setShowAdmin, isAdmin, setIsAdmin }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <img src="https://customer-assets.emergentagent.com/job_7ac0f3ca-81b2-49ce-a27b-bd65357f766a/artifacts/d670l3hu_Logo%20Hannu%20Clothes.jpeg" alt="HANNU CLOTHES" />
            <span className="logo-text">Catálogo Profesional</span>
          </div>
          
          <nav className={`nav ${isMenuOpen ? 'nav-open' : ''}`}>
            {categories.map(category => (
              <button
                key={category.id}
                className={`nav-link ${selectedCategory === category.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedCategory(category.id);
                  setIsMenuOpen(false);
                }}
              >
                {category.name}
              </button>
            ))}
          </nav>

          <div className="header-actions">
            <button className="action-btn">
              <Search size={20} />
            </button>
            <a 
              href="https://wa.me/message/MNLVUZAVGCAHH1" 
              target="_blank" 
              rel="noopener noreferrer"
              className="whatsapp-btn"
              title="¡Bienvenida a Hannuclothes!! ¿Cómo podemos ayudarte?"
            >
              <MessageCircle size={20} />
              <span>WhatsApp</span>
            </a>
            <button 
              className={`admin-btn ${showAdmin ? 'active' : ''}`}
              onClick={() => {
                setShowAdmin(!showAdmin);
                setIsAdmin(true); // Fix: Enable admin mode when accessing admin panel
              }}
            >
              <User size={20} />
              {isAdmin ? 'Admin' : 'Acceso'}
            </button>
            <button className="menu-toggle" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-text">
          <h1>HANNU CLOTHES<br />Catálogo Profesional</h1>
          <p>Descubre nuestra colección exclusiva de prendas femeninas. Sistema profesional de inventario con precios mayoristas y al por menor.</p>
          <div className="hero-features">
            <div className="feature">
              <Check size={20} />
              <span>Precios Mayorista y Detal</span>
            </div>
            <div className="feature">
              <Check size={20} />
              <span>Inventario en Tiempo Real</span>
            </div>
            <div className="feature">
              <Check size={20} />
              <span>Gestión Completa de Productos</span>
            </div>
          </div>
        </div>
        <div className="hero-image">
          <img src="https://customer-assets.emergentagent.com/job_hannu-clothing/artifacts/54sp5pdl_Enterizo%20Suelto.jpeg" alt="HANNU CLOTHES - Enterizo Elegante" />
        </div>
      </div>
    </section>
  );
};

const ProductCard = ({ product, onView, isAdmin, onEdit, onDelete }) => {
  const [showPrices, setShowPrices] = useState('retail');

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getTotalStock = () => {
    return Object.values(product.stock || {}).reduce((total, qty) => total + qty, 0);
  };

  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.image} alt={product.name} />
        {isAdmin && (
          <div className="admin-controls">
            <button className="control-btn edit" onClick={() => onEdit(product)}>
              <Edit size={16} />
            </button>
            <button className="control-btn delete" onClick={() => onDelete(product.id)}>
              <Trash2 size={16} />
            </button>
          </div>
        )}
        <div className="stock-badge">
          Stock: {getTotalStock()}
        </div>
      </div>
      <div className="product-info">
        <h3>{product.name}</h3>
        <div className="price-toggle">
          <button 
            className={`price-btn ${showPrices === 'retail' ? 'active' : ''}`}
            onClick={() => setShowPrices('retail')}
          >
            Detal
          </button>
          <button 
            className={`price-btn ${showPrices === 'wholesale' ? 'active' : ''}`}
            onClick={() => setShowPrices('wholesale')}
          >
            Mayorista
          </button>
        </div>
        <div className="prices">
          <p className="price current">
            {showPrices === 'retail' ? formatPrice(product.retail_price) : formatPrice(product.wholesale_price)}
          </p>
          <p className="price-label">
            {showPrices === 'retail' ? 'Precio al Detal' : 'Precio Mayorista'}
          </p>
        </div>
        <button 
          className="view-details-btn"
          onClick={() => onView(product)}
        >
          <Eye size={16} />
          Ver Detalles
        </button>
      </div>
    </div>
  );
};

const ProductModal = ({ product, isOpen, onClose }) => {
  const [showPrices, setShowPrices] = useState('retail');

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (!isOpen || !product) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="product-modal large" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-content">
          <div className="modal-image">
            <img src={product.image} alt={product.name} />
          </div>
          
          <div className="modal-info">
            <h2>{product.name}</h2>
            
            <div className="price-section">
              <div className="price-toggle">
                <button 
                  className={`price-btn ${showPrices === 'retail' ? 'active' : ''}`}
                  onClick={() => setShowPrices('retail')}
                >
                  Precio Detal
                </button>
                <button 
                  className={`price-btn ${showPrices === 'wholesale' ? 'active' : ''}`}
                  onClick={() => setShowPrices('wholesale')}
                >
                  Precio Mayorista
                </button>
              </div>
              <p className="modal-price">
                {showPrices === 'retail' ? formatPrice(product.retail_price) : formatPrice(product.wholesale_price)}
              </p>
              <div className="both-prices">
                <span>Detal: {formatPrice(product.retail_price)}</span>
                <span>Mayorista: {formatPrice(product.wholesale_price)}</span>
              </div>
            </div>
            
            <p className="product-description">{product.description}</p>
            
            <div className="product-details">
              <div className="detail-section">
                <h4>Especificaciones</h4>
                <p>{product.specifications}</p>
              </div>
              
              <div className="detail-section">
                <h4>Composición</h4>
                <p>{product.composition}</p>
              </div>
              
              <div className="detail-section">
                <h4>Cuidados</h4>
                <p>{product.care}</p>
              </div>
              
              <div className="detail-section">
                <h4>Política de Envíos</h4>
                <p>{product.shipping_policy}</p>
              </div>
              
              <div className="detail-section">
                <h4>Política de Cambios</h4>
                <p>{product.exchange_policy}</p>
              </div>
              
              <div className="detail-section">
                <h4>Tallas Disponibles</h4>
                <div className="size-stock-grid">
                  {product.sizes.map(size => (
                    <div key={size} className="size-stock-item">
                      <span className="size">{size}</span>
                      <span className="stock">Stock: {product.stock[size] || 0}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AdminPanel = ({ isOpen, onClose, products, setProducts }) => {
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    retail_price: '',
    wholesale_price: '',
    category: 'vestidos',
    image: '',
    composition: '',
    sizes: [],
    stock: {}
  });

  const convertGoogleDriveLink = () => {
    const currentUrl = formData.image;
    
    // Check if it's a Google Drive link
    if (currentUrl.includes('drive.google.com')) {
      const regex = /\/file\/d\/([a-zA-Z0-9_-]+)\//;
      const match = currentUrl.match(regex);
      
      if (match && match[1]) {
        const fileId = match[1];
        const directUrl = `https://drive.google.com/uc?export=view&id=${fileId}`;
        setFormData({...formData, image: directUrl});
        alert('¡Enlace convertido exitosamente! Ahora la imagen debería mostrarse correctamente.');
      } else {
        alert('No se pudo extraer el ID del archivo. Asegúrate de que sea un enlace válido de Google Drive.');
      }
    } else {
      alert('Este no parece ser un enlace de Google Drive.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      retail_price: '',
      wholesale_price: '',
      category: 'vestidos',
      image: '',
      composition: '',
      sizes: [],
      stock: {}
    });
    setEditingProduct(null);
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description,
      retail_price: product.retail_price,
      wholesale_price: product.wholesale_price,
      category: product.category,
      image: product.image,
      composition: product.composition,
      sizes: product.sizes,
      stock: product.stock
    });
  };

  const handleSave = () => {
    if (editingProduct) {
      // Update existing product
      setProducts(products.map(p => 
        p.id === editingProduct.id 
          ? { ...editingProduct, ...formData }
          : p
      ));
    } else {
      // Add new product
      const newProduct = {
        id: Date.now(),
        ...formData,
        retail_price: parseInt(formData.retail_price),
        wholesale_price: parseInt(formData.wholesale_price)
      };
      setProducts([...products, newProduct]);
    }
    resetForm();
  };

  const handleDelete = (productId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      setProducts(products.filter(p => p.id !== productId));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="admin-panel-overlay">
      <div className="admin-panel">
        <div className="admin-header">
          <h2>Panel de Administración - HANNU CLOTHES</h2>
          <button className="admin-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        
        <div className="admin-content">
          <div className="admin-form">
            <h3>{editingProduct ? 'Editar Producto' : 'Nuevo Producto'}</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Nombre del Producto</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              
              <div className="form-group">
                <label>Categoría</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                >
                  <option value="vestidos">Vestidos</option>
                  <option value="enterizos">Enterizos</option>
                  <option value="conjuntos">Conjuntos</option>
                  <option value="blusas">Blusas</option>
                  <option value="faldas">Faldas</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Precio al Detal (COP)</label>
                <input
                  type="number"
                  value={formData.retail_price}
                  onChange={(e) => setFormData({...formData, retail_price: e.target.value})}
                />
              </div>
              
              <div className="form-group">
                <label>Precio Mayorista (COP)</label>
                <input
                  type="number"
                  value={formData.wholesale_price}
                  onChange={(e) => setFormData({...formData, wholesale_price: e.target.value})}
                />
              </div>
              
              <div className="form-group full-width">
                <label>URL de Imagen</label>
                <input
                  type="url"
                  value={formData.image}
                  onChange={(e) => setFormData({...formData, image: e.target.value})}
                  placeholder="Pega aquí tu enlace de imagen"
                />
                <div className="image-helper">
                  <button 
                    type="button" 
                    className="convert-btn"
                    onClick={() => convertGoogleDriveLink()}
                  >
                    🔄 Convertir enlace de Google Drive
                  </button>
                  <small>Si usas Google Drive, pega el enlace y haz clic en "Convertir"</small>
                </div>
                {formData.image && (
                  <div className="image-preview">
                    <img src={formData.image} alt="Vista previa" />
                  </div>
                )}
              </div>
              
              <div className="form-group full-width">
                <label>Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows="3"
                />
              </div>
              
              <div className="form-group">
                <label>Composición</label>
                <input
                  type="text"
                  value={formData.composition}
                  onChange={(e) => setFormData({...formData, composition: e.target.value})}
                />
              </div>
            </div>
            
            <div className="form-actions">
              <button className="save-btn" onClick={handleSave}>
                <Save size={16} />
                {editingProduct ? 'Actualizar' : 'Guardar'} Producto
              </button>
              <button className="cancel-btn" onClick={resetForm}>
                Cancelar
              </button>
            </div>
          </div>
          
          <div className="admin-product-list">
            <h3>Productos Actuales ({products.length})</h3>
            <div className="product-list">
              {products.map(product => (
                <div key={product.id} className="admin-product-item">
                  <img src={product.image} alt={product.name} />
                  <div className="product-info">
                    <h4>{product.name}</h4>
                    <p>Detal: ${product.retail_price.toLocaleString()}</p>
                    <p>Mayorista: ${product.wholesale_price.toLocaleString()}</p>
                    <span className="category">{product.category}</span>
                  </div>
                  <div className="product-actions">
                    <button onClick={() => handleEdit(product)}>
                      <Edit size={16} />
                    </button>
                    <button onClick={() => handleDelete(product.id)}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('todos');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load products from backend
    const loadProducts = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API}/products`);
        console.log('Products loaded from backend:', response.data.length);
        
        // If no products in backend, use sample data
        if (response.data.length === 0) {
          console.log('No products in backend, using sample data');
          setProducts(sampleProducts);
        } else {
          setProducts(response.data);
        }
      } catch (e) {
        console.error('Failed to load products, using sample data:', e);
        setProducts(sampleProducts);
      } finally {
        setLoading(false);
      }
    };
    
    loadProducts();
  }, []);

  const filteredProducts = selectedCategory === 'todos' 
    ? products 
    : products.filter(product => product.category === selectedCategory);

  const openProductModal = (product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  const handleEditProduct = (product) => {
    setShowAdmin(true);
    setIsAdmin(true);
  };

  const handleDeleteProduct = (productId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      setProducts(products.filter(p => p.id !== productId));
    }
  };

  return (
    <div className="app">
      <Header 
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        showAdmin={showAdmin}
        setShowAdmin={setShowAdmin}
        isAdmin={isAdmin}
        setIsAdmin={setIsAdmin}
      />
      
      <main>
        <Hero />
        
        <section className="products catalog">
          <div className="container">
            <h2>Catálogo de Productos</h2>
            <div className="catalog-stats">
              <div className="stat">
                <span className="stat-number">{products.length}</span>
                <span className="stat-label">Productos Total</span>
              </div>
              <div className="stat">
                <span className="stat-number">{filteredProducts.length}</span>
                <span className="stat-label">Mostrando</span>
              </div>
              <div className="stat">
                <span className="stat-number">{categories.length - 1}</span>
                <span className="stat-label">Categorías</span>
              </div>
            </div>
            
            <div className="category-tabs">
              {categories.map(category => (
                <button
                  key={category.id}
                  className={`category-tab ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  {category.name}
                </button>
              ))}
            </div>
            
            <div className="products-grid">
              {loading ? (
                <div className="loading-message">
                  <div className="loading"></div>
                  <p>Cargando productos...</p>
                </div>
              ) : filteredProducts.length === 0 ? (
                <div className="no-products">
                  <p>No hay productos en esta categoría</p>
                </div>
              ) : (
                filteredProducts.map(product => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onView={openProductModal}
                    isAdmin={isAdmin}
                    onEdit={handleEditProduct}
                    onDelete={handleDeleteProduct}
                  />
                ))
              )}
            </div>
          </div>
        </section>
        
        <section className="featured-product">
          <div className="container">
            <div className="featured-content">
              <div className="featured-text">
                <h2>Nuestra Pasión por la Moda</h2>
                <p>
                  En HANNU CLOTHES, cada prenda refleja nuestra dedicación por la elegancia y la calidad. 
                  Creamos piezas únicas que realzan la belleza natural de cada mujer, combinando tendencias 
                  actuales con diseños atemporales.
                </p>
                <p>
                  Nuestro compromiso es ofrecer un catálogo profesional que facilite la gestión de inventario 
                  mientras mantenemos los más altos estándares de calidad y servicio.
                </p>
              </div>
              <div className="featured-image">
                <img src="https://customer-assets.emergentagent.com/job_hannu-clothing/artifacts/rvmnvnxx_Vestido%20Sorelle%20Rosado.jpeg" alt="HANNU CLOTHES - Vestido Sorelle Rosado" />
              </div>
            </div>
          </div>
        </section>
        
        <section className="policies">
          <div className="container">
            <h2>Políticas de la Empresa</h2>
            <div className="policies-grid">
              
              <div className="policy-card">
                <h3>💳 Métodos de Pago</h3>
                <ul>
                  <li><strong>En Medellín:</strong> Contra entrega 🏡</li>
                  <li><strong>Para el resto del país 🇨🇴:</strong> Pago anticipado por medio de Bancolombia o Davivienda</li>
                </ul>
              </div>

              <div className="policy-card">
                <h3>💕 Política de Envío</h3>
                <p>
                  Nuestros envíos se realizan al día hábil siguiente de realizar tu compra 
                  (tener en cuenta que la transportadora tarda 1 a 2 días hábiles aproximadamente).
                </p>
              </div>

              <div className="policy-card">
                <h3>🤍 Política de Cambio</h3>
                <p><strong>Para los cambios solo se dan 2 días.</strong></p>
                <ul>
                  <li>Solo se hacen cambios en vestidos, blusas, pantalones, faldas y shorts</li>
                  <li>Siempre y cuando la prenda esté en buen estado</li>
                  <li><strong>Bodys NO tienen cambio</strong> (son prendas íntimas)</li>
                  <li><strong>Prendas blancas NO tienen cambio</strong></li>
                  <li>No se corre con gastos de envío, estos los debe asumir el cliente</li>
                  <li>Se debe cambiar por algo de igual o mayor valor (no se reembolsa dinero ni se usa la diferencia para pagar domicilio)</li>
                </ul>
              </div>

              <div className="policy-card">
                <h3>🛍 Política de Ventas al Por Mayor</h3>
                <ul>
                  <li><strong>Primera compra:</strong> Mínimo 6 prendas (pueden ser surtidas)</li>
                  <li><strong>Compras siguientes:</strong> Mínimo 3 prendas</li>
                  <li><strong>Importante:</strong> Si pasa más de un mes sin comprar, deben ser nuevamente 6 prendas para obtener precio al por mayor</li>
                </ul>
              </div>

            </div>
          </div>
        </section>
      </main>
      
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>HANNU CLOTHES</h4>
              <p>Sistema profesional de catálogo para moda femenina.</p>
              <div className="footer-logo">
                <img src="https://customer-assets.emergentagent.com/job_7ac0f3ca-81b2-49ce-a27b-bd65357f766a/artifacts/d670l3hu_Logo%20Hannu%20Clothes.jpeg" alt="HANNU CLOTHES" />
              </div>
              <div className="social-links">
                <a href="https://instagram.com/hannuclothes" target="_blank" rel="noopener noreferrer" className="social-link">
                  <Instagram size={20} />
                  <span>@hannuclothes</span>
                </a>
                <a href="https://facebook.com/hannuclothes" target="_blank" rel="noopener noreferrer" className="social-link">
                  <Facebook size={20} />
                  <span>@hannuclothes</span>
                </a>
              </div>
            </div>
            
            <div className="footer-section">
              <h4>Categorías</h4>
              <ul>
                <li>Vestidos</li>
                <li>Enterizos</li>
                <li>Conjuntos</li>
                <li>Blusas</li>
                <li>Faldas & Pantalones</li>
              </ul>
            </div>
            
            <div className="footer-section">
              <h4>Información</h4>
              <ul>
                <li>Precios Mayorista</li>
                <li>Precios al Detal</li>
                <li>Gestión de Inventario</li>
                <li>Políticas de Envío</li>
                <li>Políticas de Cambio</li>
              </ul>
            </div>
            
            <div className="footer-section">
              <h4>Contacto</h4>
              <div className="contact-info">
                <div className="contact-item">
                  <Phone size={16} />
                  <span>+57 305 451 2482</span>
                  <small>(WhatsApp Business)</small>
                </div>
                <div className="contact-item">
                  <MapPin size={16} />
                  <span>Medellín, Colombia</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2024 HANNU CLOTHES - Sistema de Catálogo Profesional. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
      
      <ProductModal
        product={selectedProduct}
        isOpen={isProductModalOpen}
        onClose={() => setIsProductModalOpen(false)}
      />
      
      <AdminPanel
        isOpen={showAdmin && isAdmin}
        onClose={() => setShowAdmin(false)}
        products={products}
        setProducts={setProducts}
      />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;