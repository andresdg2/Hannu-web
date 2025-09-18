import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { ShoppingCart, User, Search, Menu, X, Heart, Star, ArrowRight, Check, Phone, Mail, MapPin, Plus, Edit, Trash2, Upload, Save, Eye, MessageCircle, Instagram, Facebook } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sample product data with multiple images and colors
const sampleProducts = [
  {
    id: 1,
    name: "Vestido Rosa Elegante",
    description: "Vestido elegante perfecto para ocasiones especiales. Confeccionado en tela de alta calidad con acabados refinados.",
    retail_price: 150000,
    wholesale_price: 105000,
    category: "vestidos",
    images: [
      "https://i.ibb.co/ckRPK0cn/Vestido-Velvet.jpg",
      "https://customer-assets.emergentagent.com/job_hannu-clothing/artifacts/rvmnvnxx_Vestido%20Sorelle%20Rosado.jpeg"
    ],
    colors: ["Rosa", "Beige"],
    specifications: "Vestido de corte A, manga corta, cuello redondo, cierre posterior invisible",
    composition: "95% Algodón, 5% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura media",
    sizes: ["XS", "S", "M", "L", "XL"]
  },
  {
    id: 2,
    name: "Blusa Rayas Esencial",
    description: "Blusa de rayas clásica que combina con todo. Ideal para el día a día con un toque elegante y versátil.",
    retail_price: 75000,
    wholesale_price: 52500,
    category: "blusas",
    images: [
      "https://i.ibb.co/ckRPK0cn/Vestido-Velvet.jpg"
    ],
    colors: ["Blanco con rayas negras"],
    specifications: "Blusa de rayas horizontales, manga larga, cuello camisero, botones frontales",
    composition: "100% Algodón orgánico",
    care: "Lavar a máquina en agua tibia, secar al aire, planchar del revés",
    sizes: ["XS", "S", "M", "L", "XL"]
  },
  {
    id: 3,
    name: "Enterizo Elegante Negro",
    description: "Enterizo sofisticado perfecto para eventos especiales. Diseño moderno con corte favorecedor.",
    retail_price: 185000,
    wholesale_price: 129500,
    category: "enterizos",
    images: [
      "https://customer-assets.emergentagent.com/job_hannu-clothing/artifacts/abfuz73m_Vestido%20Sorelle%20Negro.jpeg"
    ],
    colors: ["Negro"],
    specifications: "Enterizo de pierna ancha, tirantes ajustables, cintura marcada, bolsillos laterales",
    composition: "88% Poliéster, 12% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura baja",
    sizes: ["XS", "S", "M", "L", "XL"]
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
              <span>Confeccionamos modelos específicos</span>
            </div>
            <div className="feature">
              <Check size={20} />
              <span>Gestión Completa de Productos</span>
            </div>
          </div>
        </div>
        <div className="hero-image">
          <img src="https://customer-assets.emergentagent.com/job_hannu-clothing/artifacts/abfuz73m_Vestido%20Sorelle%20Negro.jpeg" alt="HANNU CLOTHES - Vestido Sorelle Negro" />
        </div>
      </div>
    </section>
  );
};

const ProductCard = ({ product, onView, isAdmin, onEdit, onDelete }) => {
  const [showPrices, setShowPrices] = useState('retail');
  const [imageError, setImageError] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const formatPrice = (price) => {
    // Ensure price is a number
    const numPrice = typeof price === 'number' ? price : parseInt(price) || 0;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(numPrice);
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const handleImageLoad = () => {
    setImageError(false);
  };

  const currentImage = product.images && product.images.length > 0 ? product.images[currentImageIndex] : product.image;

  const nextImage = () => {
    if (product.images && product.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % product.images.length);
    }
  };

  const prevImage = () => {
    if (product.images && product.images.length > 1) {
      setCurrentImageIndex((prev) => (prev - 1 + product.images.length) % product.images.length);
    }
  };

  return (
    <div className="product-card">
      <div className="product-image">
        {!imageError ? (
          <>
            <img 
              src={currentImage} 
              alt={product.name}
              onError={handleImageError}
              onLoad={handleImageLoad}
              crossOrigin="anonymous"
            />
            {product.images && product.images.length > 1 && (
              <>
                <button className="image-nav prev" onClick={prevImage}>‹</button>
                <button className="image-nav next" onClick={nextImage}>›</button>
                <div className="image-dots">
                  {product.images.map((_, index) => (
                    <span 
                      key={index} 
                      className={`dot ${index === currentImageIndex ? 'active' : ''}`}
                      onClick={() => setCurrentImageIndex(index)}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="image-placeholder">
            <div className="placeholder-content">
              <span>📷</span>
              <p>Imagen no disponible</p>
            </div>
          </div>
        )}
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
        {product.colors && product.colors.length > 0 && (
          <div className="colors-badge">
            {product.colors.length} {product.colors.length === 1 ? 'Color' : 'Colores'}
          </div>
        )}
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
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (!isOpen || !product) return null;

  const currentImage = product.images && product.images.length > 0 ? product.images[currentImageIndex] : product.image;

  const nextImage = () => {
    if (product.images && product.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % product.images.length);
    }
  };

  const prevImage = () => {
    if (product.images && product.images.length > 1) {
      setCurrentImageIndex((prev) => (prev - 1 + product.images.length) % product.images.length);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="product-modal large" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-content">
          <div className="modal-image">
            <img src={currentImage} alt={product.name} />
            {product.images && product.images.length > 1 && (
              <>
                <button className="modal-image-nav prev" onClick={prevImage}>‹</button>
                <button className="modal-image-nav next" onClick={nextImage}>›</button>
                <div className="modal-image-dots">
                  {product.images.map((_, index) => (
                    <span 
                      key={index} 
                      className={`modal-dot ${index === currentImageIndex ? 'active' : ''}`}
                      onClick={() => setCurrentImageIndex(index)}
                    />
                  ))}
                </div>
              </>
            )}
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
              
              {product.colors && product.colors.length > 0 && (
                <div className="detail-section">
                  <h4>Colores Disponibles</h4>
                  <div className="colors-list">
                    {product.colors.map((color, index) => (
                      <span key={index} className="color-tag">
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="detail-section">
                <h4>Tallas Disponibles</h4>
                <div className="sizes-list">
                  {product.sizes.map(size => (
                    <span key={size} className="size-tag">
                      {size}
                    </span>
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

const AdminPanel = ({ isOpen, onClose, products, setProducts, productToEdit }) => {
  const [editingProduct, setEditingProduct] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    retail_price: '',
    wholesale_price: '',
    category: 'vestidos',
    images: [''],
    colors: [''],
    composition: '',
    sizes: ['']
  });

  // Effect to handle productToEdit from parent component
  useEffect(() => {
    if (productToEdit) {
      handleEdit(productToEdit);
    }
  }, [productToEdit]);

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      retail_price: '',
      wholesale_price: '',
      category: 'vestidos',
      images: [''],
      colors: [''],
      composition: '',
      sizes: ['']
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
      images: product.images && product.images.length > 0 ? product.images : [product.image || ''],
      colors: product.colors || [''],
      composition: product.composition,
      sizes: product.sizes && product.sizes.length > 0 ? product.sizes : ['']
    });
  };

  const saveProduct = async () => {
    setSaving(true);
    try {
      // Get admin token
      const token = localStorage.getItem('adminToken');
      if (!token) {
        alert('Error: No se encontró token de administrador');
        return;
      }

      // Validate form data
      if (!formData.name || !formData.description || !formData.retail_price || !formData.wholesale_price) {
        alert('Por favor completa todos los campos obligatorios');
        return;
      }

      // Prepare product data
      const productData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        retail_price: parseInt(formData.retail_price),
        wholesale_price: parseInt(formData.wholesale_price),
        category: formData.category,
        images: formData.images.filter(img => img.trim() !== ''),
        colors: formData.colors.filter(color => color.trim() !== ''),
        sizes: formData.sizes.filter(size => size.trim() !== ''),
        composition: formData.composition.trim(),
        specifications: `${formData.category} de alta calidad`,
        care: 'Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura media',
        shipping_policy: 'Envío nacional 2-5 días hábiles',
        exchange_policy: 'Cambios hasta 15 días después de la compra'
      };

      // Ensure at least one image
      if (productData.images.length === 0) {
        productData.images = ['https://via.placeholder.com/400x400?text=No+Image'];
      }

      // Set main image for backward compatibility
      productData.image = productData.images[0];

      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      let response;
      if (editingProduct) {
        // Update existing product
        response = await axios.put(`${API}/products/${editingProduct.id}`, productData, { headers });
        // Update in products list
        setProducts(products.map(p => p.id === editingProduct.id ? response.data : p));
        alert('✅ Producto actualizado correctamente');
      } else {
        // Create new product
        response = await axios.post(`${API}/products`, productData, { headers });
        // Add to products list
        setProducts([...products, response.data]);
        alert('✅ Producto creado correctamente');
      }

      console.log('Product saved:', response.data);
      resetForm();
      onClose();

    } catch (error) {
      console.error('Error saving product:', error);
      if (error.response?.status === 401) {
        alert('Error: Sesión de administrador expirada. Por favor vuelve a acceder.');
        localStorage.removeItem('adminToken');
      } else if (error.response?.data?.detail) {
        alert(`Error: ${error.response.data.detail}`);
      } else {
        alert('Error al guardar el producto. Por favor intenta de nuevo.');
      }
    } finally {
      setSaving(false);
    }
  };

  const addImageField = () => {
    setFormData({...formData, images: [...formData.images, '']});
  };

  const removeImageField = (index) => {
    if (formData.images.length > 1) {
      const newImages = formData.images.filter((_, i) => i !== index);
      setFormData({...formData, images: newImages});
    }
  };

  const updateImage = (index, value) => {
    const newImages = [...formData.images];
    newImages[index] = value;
    setFormData({...formData, images: newImages});
  };

  const addColorField = () => {
    setFormData({...formData, colors: [...formData.colors, '']});
  };

  const removeColorField = (index) => {
    if (formData.colors.length > 1) {
      const newColors = formData.colors.filter((_, i) => i !== index);
      setFormData({...formData, colors: newColors});
    }
  };

  const updateColor = (index, value) => {
    const newColors = [...formData.colors];
    newColors[index] = value;
    setFormData({...formData, colors: newColors});
  };

  const addSizeField = () => {
    setFormData({...formData, sizes: [...formData.sizes, '']});
  };

  const removeSizeField = (index) => {
    if (formData.sizes.length > 1) {
      const newSizes = formData.sizes.filter((_, i) => i !== index);
      setFormData({...formData, sizes: newSizes});
    }
  };

  const updateSize = (index, value) => {
    const newSizes = [...formData.sizes];
    newSizes[index] = value;
    setFormData({...formData, sizes: newSizes});
  };

  const convertGoogleDriveLink = (imageUrl) => {
    if (imageUrl.includes('drive.google.com')) {
      const regex = /\/file\/d\/([a-zA-Z0-9_-]+)\//;
      const match = imageUrl.match(regex);
      
      if (match && match[1]) {
        const fileId = match[1];
        return `https://drive.google.com/uc?export=view&id=${fileId}`;
      }
    }
    return imageUrl;
  };

  const testImageUrl = async (url) => {
    if (!url) {
      alert('URL vacía');
      return;
    }

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        alert('✅ ¡La imagen carga correctamente!');
      };
      
      img.onerror = () => {
        alert('❌ Error: No se puede cargar la imagen.');
      };
      
      img.src = url;
      
    } catch (error) {
      alert('Error al probar la imagen: ' + error.message);
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
              
              <div className="form-group full-width">
                <label>Imágenes del Producto</label>
                {formData.images.map((image, index) => (
                  <div key={index} className="image-input-group">
                    <input
                      type="url"
                      value={image}
                      onChange={(e) => updateImage(index, e.target.value)}
                      placeholder={`URL de imagen ${index + 1}`}
                    />
                    <div className="image-controls">
                      <button 
                        type="button" 
                        className="convert-btn-small"
                        onClick={() => updateImage(index, convertGoogleDriveLink(image))}
                      >
                        🔄
                      </button>
                      <button 
                        type="button" 
                        className="test-btn-small"
                        onClick={() => testImageUrl(image)}
                      >
                        🧪
                      </button>
                      {formData.images.length > 1 && (
                        <button 
                          type="button" 
                          className="remove-btn"
                          onClick={() => removeImageField(index)}
                        >
                          ❌
                        </button>
                      )}
                    </div>
                    {image && (
                      <div className="mini-preview">
                        <img src={image} alt={`Preview ${index + 1}`} onError={(e) => e.target.style.display = 'none'} />
                      </div>
                    )}
                  </div>
                ))}
                <button type="button" className="add-btn" onClick={addImageField}>
                  ➕ Agregar Imagen
                </button>
              </div>
              
              <div className="form-group full-width">
                <label>Colores Disponibles</label>
                {formData.colors.map((color, index) => (
                  <div key={index} className="color-input-group">
                    <input
                      type="text"
                      value={color}
                      onChange={(e) => updateColor(index, e.target.value)}
                      placeholder={`Color ${index + 1}`}
                    />
                    {formData.colors.length > 1 && (
                      <button 
                        type="button" 
                        className="remove-btn"
                        onClick={() => removeColorField(index)}
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))}
                <button type="button" className="add-btn" onClick={addColorField}>
                  ➕ Agregar Color
                </button>
              </div>
              
              <div className="form-group full-width">
                <label>Tallas Disponibles</label>
                {formData.sizes.map((size, index) => (
                  <div key={index} className="size-input-group">
                    <input
                      type="text"
                      value={size}
                      onChange={(e) => updateSize(index, e.target.value)}
                      placeholder={`Talla ${index + 1} (ej: S, M, L, XL)`}
                    />
                    {formData.sizes.length > 1 && (
                      <button 
                        type="button" 
                        className="remove-btn"
                        onClick={() => removeSizeField(index)}
                      >
                        ❌
                      </button>
                    )}
                  </div>
                ))}
                <button type="button" className="add-btn" onClick={addSizeField}>
                  ➕ Agregar Talla
                </button>
              </div>
            </div>
            
            <div className="form-actions">
              <button 
                className="save-btn" 
                onClick={saveProduct}
                disabled={saving}
              >
                <Save size={16} />
                {saving ? 'Guardando...' : (editingProduct ? 'Actualizar' : 'Guardar')} Producto
              </button>
              <button className="cancel-btn" onClick={resetForm}>
                Cancelar
              </button>
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
  const [productToEdit, setProductToEdit] = useState(null);

  useEffect(() => {
    // Load products from backend
    const loadProducts = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API}/products`);
        console.log('Products loaded from backend:', response.data.length);
        
        if (response.data.length > 0) {
          setProducts(response.data);
        } else {
          console.log('No products in backend, using sample data');
          setProducts(sampleProducts);
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

  const loginAdmin = async () => {
    try {
      const response = await axios.post(`${API}/admin/login`, {
        username: 'admin',
        password: 'admin123'
      });
      
      const token = response.data.access_token;
      localStorage.setItem('adminToken', token);
      alert('✅ Sesión de administrador iniciada correctamente');
      return token;
    } catch (error) {
      console.error('Error logging in as admin:', error);
      alert('Error al iniciar sesión de administrador');
      return null;
    }
  };

  const ensureAdminAuth = async () => {
    const storedToken = localStorage.getItem('adminToken');
    if (!storedToken) {
      const token = await loginAdmin();
      return token;
    }
    return storedToken;
  };

  const filteredProducts = selectedCategory === 'todos' 
    ? products 
    : products.filter(product => product.category === selectedCategory);

  const openProductModal = (product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  const handleEditProduct = (product) => {
    setProductToEdit(product);
    setShowAdmin(true);
    setIsAdmin(true);
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      try {
        const token = localStorage.getItem('adminToken');
        if (!token) {
          alert('Error: No se encontró token de administrador');
          return;
        }

        const headers = {
          'Authorization': `Bearer ${token}`
        };

        await axios.delete(`${API}/products/${productId}`, { headers });
        setProducts(products.filter(p => p.id !== productId));
        alert('✅ Producto eliminado correctamente');
      } catch (error) {
        console.error('Error deleting product:', error);
        if (error.response?.status === 401) {
          alert('Error: Sesión de administrador expirada. Por favor vuelve a acceder.');
          localStorage.removeItem('adminToken');
        } else {
          alert('Error al eliminar el producto. Por favor intenta de nuevo.');
        }
      }
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
        
        <section className="contact-section">
          <div className="container">
            <div className="contact-header">
              <h2>Contáctanos</h2>
              <p>Estamos aquí para ayudarte</p>
            </div>
            
            <div className="contact-grid">
              
              <div className="contact-card whatsapp-card">
                <div className="contact-icon">
                  <MessageCircle size={40} />
                </div>
                <h3>WhatsApp Business</h3>
                <p className="contact-number">+57 305 451 2482</p>
                <p className="contact-subtitle">Atendemos a nuestras clientas</p>
                <a 
                  href="https://wa.me/message/MNLVUZAVGCAHH1" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="contact-btn whatsapp-btn-large"
                >
                  Escribir ahora
                </a>
              </div>

              <div className="contact-card location-card">
                <div className="contact-icon">
                  <MapPin size={40} />
                </div>
                <h3>Ubicación</h3>
                <p className="contact-location">Medellín, Colombia</p>
                <p className="contact-subtitle">Envíos a todo el país</p>
              </div>

              <div className="contact-card instagram-card">
                <div className="contact-icon">
                  <Instagram size={40} />
                </div>
                <h3>Instagram</h3>
                <p className="contact-handle">@hannuclothes</p>
                <p className="contact-subtitle">Síguenos para novedades</p>
                <a 
                  href="https://instagram.com/hannuclothes" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="contact-btn instagram-btn"
                >
                  Seguir
                </a>
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
        onClose={() => {
          setShowAdmin(false);
          setProductToEdit(null);
        }}
        products={products}
        setProducts={setProducts}
        productToEdit={productToEdit}
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