import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { ShoppingCart, User, Search, Menu, X, Heart, Star, ArrowRight, Check, Phone, Mail, MapPin, Plus, Edit, Trash2, Upload, Save, Eye, MessageCircle, Instagram, Facebook } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// SmartImage component with improved fallback handling
const SmartImage = ({ originalSrc, alt, alternativeUrl, productName }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const [currentSrc, setCurrentSrc] = useState(originalSrc);
  const [loadAttempt, setLoadAttempt] = useState(0);

  const handleImageError = () => {
    console.log(`Image load failed for ${productName}:`, currentSrc);
    
    if (loadAttempt === 0 && alternativeUrl && currentSrc === originalSrc) {
      // First failure - try alternative URL
      console.log(`Trying alternative URL for ${productName}:`, alternativeUrl);
      setCurrentSrc(alternativeUrl);
      setLoadAttempt(1);
      setImageLoading(true);
    } else if (loadAttempt === 1) {
      // Second failure - try original URL again with cache buster
      console.log(`Retrying original with cache buster for ${productName}`);
      setCurrentSrc(`${originalSrc}?t=${Date.now()}`);
      setLoadAttempt(2);
      setImageLoading(true);
    } else {
      // Final failure - show placeholder
      console.log(`All attempts failed for ${productName}, showing placeholder`);
      setImageError(true);
      setImageLoading(false);
    }
  };

  const handleImageLoad = () => {
    console.log(`Image loaded successfully for ${productName}:`, currentSrc);
    setImageError(false);
    setImageLoading(false);
  };

  // Reset when originalSrc changes
  useEffect(() => {
    setCurrentSrc(originalSrc);
    setImageError(false);
    setImageLoading(true);
    setLoadAttempt(0);
  }, [originalSrc]);
  
  // Add timeout for loading state
  useEffect(() => {
    if (imageLoading) {
      const timeout = setTimeout(() => {
        if (imageLoading) {
          console.log(`Loading timeout for ${productName}, showing placeholder`);
          setImageError(true);
          setImageLoading(false);
        }
      }, 15000); // 15 second timeout
      
      return () => clearTimeout(timeout);
    }
  }, [imageLoading, productName]);

  if (imageError) {
    return (
      <div className="image-placeholder">
        <div className="placeholder-content">
          <span>👗</span>
          <p><strong>{productName}</strong></p>
          <p>HANNU CLOTHES</p>
          <p className="placeholder-hint">
            Imagen próximamente disponible
          </p>
          <div className="placeholder-actions">
            <button 
              className="open-btn"
              onClick={() => {
                const urlToOpen = originalSrc.includes('proxy-image') 
                  ? decodeURIComponent(originalSrc.split('url=')[1]) 
                  : originalSrc;
                window.open(urlToOpen, '_blank');
              }}
            >
              📸 Ver Imagen
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {imageLoading && (
        <div className="image-loading">
          <div className="loading-spinner"></div>
          <p>Cargando imagen...</p>
        </div>
      )}
      <img 
        src={currentSrc} 
        alt={alt}
        onError={handleImageError}
        onLoad={handleImageLoad}
        style={{ display: imageLoading ? 'none' : 'block' }}
        crossOrigin="anonymous"
      />
    </>
  );
};

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
  { id: "blusas", name: "Tops & Bodys", image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85" },
  { id: "faldas", name: "Faldas & Pantalones", image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85" }
];

const Header = ({ selectedCategory, setSelectedCategory, showAdmin, setShowAdmin, isAdmin, setIsAdmin, searchQuery, setSearchQuery, showSearch, setShowSearch }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showMainMenu, setShowMainMenu] = useState(false);

  const scrollToSection = (sectionId) => {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
    setShowMainMenu(false);
  };

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
            <button 
              className={`action-btn ${showSearch ? 'active' : ''}`}
              onClick={() => setShowSearch(!showSearch)}
            >
              <Search size={20} />
            </button>
            {showSearch && (
              <div className="search-input-container">
                <input
                  type="text"
                  placeholder="Buscar productos..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                  autoFocus
                />
              </div>
            )}
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
      
      {/* Menú eliminado - se usará el menú original */}
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

  // Función mejorada para obtener imagen con múltiples respaldos
  const getValidImage = () => {
    const productName = encodeURIComponent(product.name);
    const defaultImage = `https://via.placeholder.com/400x400/f8b4d1/333333?text=${productName}`;
    
    // Si tiene array de imágenes, usar esa
    if (product.images && product.images.length > 0) {
      const img = product.images[currentImageIndex];
      if (img && img.trim() !== '') {
        return getOptimizedImageUrl(img);
      }
    }
    
    // Si solo tiene imagen singular
    if (product.image && product.image.trim() !== '') {
      return getOptimizedImageUrl(product.image);
    }
    
    return defaultImage;
  };
  
  // Función para convertir URLs problemáticas a formatos mejores
  const getOptimizedImageUrl = (originalUrl) => {
    if (!originalUrl) return originalUrl;
    
    // Para PostImg i.postimg.cc, convertir a formato directo
    if (originalUrl.includes('i.postimg.cc/')) {
      // Extraer el ID y nombre de archivo de la URL de PostImg
      const match = originalUrl.match(/i\.postimg\.cc\/([a-zA-Z0-9]+)\/(.+?)(\?.*)?$/);
      if (match) {
        const [, imageId, filename] = match;
        // Convertir a URL directa de PostImg que evita algunos problemas de CORS
        return `https://postimg.cc/${imageId}/${filename}`;
      }
    }
    
    return originalUrl;
  };
  
  // Función para obtener URL alternativa como respaldo
  const getAlternativeImage = (originalUrl) => {
    if (!originalUrl) return null;
    
    // Para PostImg, intentar diferentes formatos de URL
    if (originalUrl.includes('postimg.cc')) {
      // Si es i.postimg.cc, intentar sin el subdominio 'i'
      if (originalUrl.includes('i.postimg.cc')) {
        return originalUrl.replace('i.postimg.cc', 'postimg.cc');
      }
      // Si es postimg.cc, intentar con 'i' subdominio
      return originalUrl.replace('postimg.cc', 'i.postimg.cc');
    }
    
    return null;
  };

  const currentImage = getValidImage();

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
        <SmartImage 
          originalSrc={currentImage}
          alt={product.name}
          alternativeUrl={getAlternativeImage(currentImage)}
          productName={product.name}
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
                  onClick={() => {
                    setCurrentImageIndex(index);
                  }}
                />
              ))}
            </div>
          </>
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
              {product.composition && (
                <div className="detail-section">
                  <h4>Composición</h4>
                  <p>{product.composition}</p>
                </div>
              )}

              <div className="detail-section">
                <h4>📦 Entrega Inmediata 💖</h4>
                <div className="delivery-info">
                  <p>LAS PRENDAS PARA ENTREGA INMEDIATA ESTÁN EN NUESTRAS 2 HISTORIAS DESTACADAS DE INSTAGRAM</p>
                  <a href="https://instagram.com/hannuclothes" target="_blank" rel="noopener noreferrer" className="instagram-link-small">
                    <Instagram size={16} />
                    @hannuclothes
                  </a>
                </div>
              </div>

              <div className="detail-section">
                <h4>💳 Métodos de Pago</h4>
                <div className="payment-methods">
                  <div className="payment-method">
                    <strong>📍 En Medellín:</strong> Contra entrega 🏡
                  </div>
                  <div className="payment-method">
                    <strong>🇨🇴 Resto del país:</strong> Pago anticipado por Bancolombia o Davivienda
                  </div>
                </div>
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
  const [showManagerLogin, setShowManagerLogin] = useState(true);
  const [isManagerAuthenticated, setIsManagerAuthenticated] = useState(false);
  const [showMassUpload, setShowMassUpload] = useState(false);
  const [showPasswordRecovery, setShowPasswordRecovery] = useState(false);
  const [recoveryEmail, setRecoveryEmail] = useState('');
  const [massUploadFiles, setMassUploadFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [managerCredentials, setManagerCredentials] = useState({
    username: '',
    password: ''
  });
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    retail_price: '',
    wholesale_price: '',
    category: 'vestidos',
    images: [''],
    colors: '',  // Cambiado a string único
    composition: '',
    sizes: ''    // Cambiado a string único
  });

  // Effect to handle productToEdit from parent component
  useEffect(() => {
    if (productToEdit) {
      handleEdit(productToEdit);
    }
  }, [productToEdit]);

  // Check if manager is already authenticated
  useEffect(() => {
    const savedAuth = localStorage.getItem('managerAuthenticated');
    if (savedAuth === 'true') {
      setIsManagerAuthenticated(true);
      setShowManagerLogin(false);
    }
  }, []);

  const authenticateManager = async () => {
    // Manager credentials - you can change these
    const validCredentials = [
      { username: 'manager', password: 'hannu2024' },
      { username: 'admin', password: 'admin123' } // Mantener admin como fallback
    ];

    const isValid = validCredentials.some(cred => 
      cred.username === managerCredentials.username && 
      cred.password === managerCredentials.password
    );

    if (isValid) {
      setIsManagerAuthenticated(true);
      setShowManagerLogin(false);
      localStorage.setItem('managerAuthenticated', 'true');
      localStorage.setItem('managerUsername', managerCredentials.username);
      alert('✅ Acceso de manager autorizado correctamente');
    } else {
      alert('❌ Credenciales incorrectas. Contacta al administrador del sistema.');
    }
  };

  const logoutManager = () => {
    setIsManagerAuthenticated(false);
    setShowManagerLogin(true);
    localStorage.removeItem('managerAuthenticated');
    localStorage.removeItem('managerUsername');
    localStorage.removeItem('adminToken');
    onClose();
  };

  const handlePasswordRecovery = () => {
    const authorizedEmails = ['judaesk8@gmail.com', 'catagui01@gmail.com'];
    
    if (!recoveryEmail) {
      alert('Por favor ingresa tu email');
      return;
    }
    
    if (!authorizedEmails.includes(recoveryEmail.toLowerCase())) {
      alert('Email no autorizado para recuperación de contraseña');
      return;
    }
    
    // Simular envío de email
    alert(`✅ Se han enviado las credenciales de acceso a ${recoveryEmail}\n\nUsuario: manager\nContraseña: hannu2024`);
    setShowPasswordRecovery(false);
    setRecoveryEmail('');
  };

  // Lista FINAL de productos que necesitan imágenes (solo 4 restantes)
  const missingImageProducts = [
    "Babeado Corto", "Nieve", "Sol", "Tira Encaje B"
  ];

  const handleMassUpload = async () => {
    if (massUploadFiles.length === 0) {
      alert('Por favor selecciona archivos para subir');
      return;
    }

    try {
      setSaving(true);
      setUploadProgress({ current: 0, total: massUploadFiles.length });

      // Obtener token de admin
      let token = localStorage.getItem('adminToken');
      if (!token) {
        token = await loginAdmin();
        if (!token) {
          alert('❌ Error: No se pudo obtener autenticación de administrador');
          return;
        }
      }

      const formData = new FormData();
      const productNames = [];

      massUploadFiles.forEach((fileData) => {
        formData.append('files', fileData.file);
        productNames.push(fileData.productName);
      });

      formData.append('product_names', productNames.join(','));

      const response = await axios.post(`${API}/admin/upload-images`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      const results = response.data;
      
      // Mostrar resultados
      const successCount = results.successful_uploads;
      const totalCount = results.total_files;
      
      if (successCount === totalCount) {
        alert(`🎉 ¡Éxito total! ${successCount}/${totalCount} imágenes subidas correctamente`);
      } else {
        alert(`⚠️ Parcialmente exitoso: ${successCount}/${totalCount} imágenes subidas. Revisa los errores.`);
      }

      // Mostrar detalles
      console.log('Resultados de carga masiva:', results);
      
      // Recargar productos
      const refreshResponse = await axios.get(`${API}/products?limit=1000`);
      setProducts(refreshResponse.data);

      // Limpiar estado
      setMassUploadFiles([]);
      setShowMassUpload(false);

    } catch (error) {
      console.error('Error en carga masiva:', error);
      alert(`❌ Error en carga masiva: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSaving(false);
      setUploadProgress(null);
    }
  };

  const handleFileSelection = (event) => {
    const files = Array.from(event.target.files);
    const newFiles = files.map(file => ({
      file,
      productName: '',
      preview: URL.createObjectURL(file)
    }));
    setMassUploadFiles(newFiles);
  };

  const updateProductName = (index, name) => {
    const updated = [...massUploadFiles];
    updated[index].productName = name;
    setMassUploadFiles(updated);
  };

  const loginAdmin = async () => {
    try {
      const response = await axios.post(`${API}/admin/login`, {
        username: 'admin',
        password: 'admin123'
      });
      
      const token = response.data.access_token;
      localStorage.setItem('adminToken', token);
      console.log('✅ Admin logged in successfully');
      return token;
    } catch (error) {
      console.error('Error logging in as admin:', error);
      return null;
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      retail_price: '',
      wholesale_price: '',
      category: 'vestidos',
      images: [''],
      colors: '',  // String único
      composition: '',
      sizes: ''    // String único
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
      colors: Array.isArray(product.colors) ? product.colors.join(', ') : (product.colors || ''),
      composition: product.composition,
      sizes: Array.isArray(product.sizes) ? product.sizes.join(', ') : (product.sizes || '')
    });
  };

  const saveProduct = async () => {
    console.log('🚀 INICIANDO GUARDADO DE PRODUCTO');
    setSaving(true);
    
    try {
      // Forzar nueva autenticación cada vez
      console.log('🔐 Iniciando sesión de administrador...');
      const token = await loginAdmin();
      if (!token) {
        alert('❌ Error: No se pudo obtener token de administrador');
        return;
      }
      console.log('✅ Token obtenido correctamente');

      // Validar campos obligatorios
      if (!formData.name || !formData.description || !formData.retail_price || !formData.wholesale_price) {
        alert('❌ Por favor completa todos los campos obligatorios: nombre, descripción, precio detal y precio mayorista');
        return;
      }

      // Preparar datos del producto
      const productData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        retail_price: parseInt(formData.retail_price),
        wholesale_price: parseInt(formData.wholesale_price),
        category: formData.category,
        images: formData.images.filter(img => img.trim() !== ''),
        colors: formData.colors.split(',').map(c => c.trim()).filter(c => c !== ''),
        sizes: formData.sizes.split(',').map(s => s.trim()).filter(s => s !== ''),
        composition: formData.composition.trim(),
        specifications: `${formData.category} de alta calidad`,
        care: 'Lavar a máquina en agua fría, no usar blanqueador, planchar a temperatura media',
        shipping_policy: 'Envío nacional 2-5 días hábiles',
        exchange_policy: 'Cambios hasta 15 días después de la compra'
      };

      // Asegurar al menos una imagen
      if (productData.images.length === 0) {
        productData.images = ['https://via.placeholder.com/400x400/f8b4d1/ffffff?text=HANNU+CLOTHES'];
      }
      productData.image = productData.images[0]; // Para compatibilidad

      console.log('📦 Datos del producto preparados:', productData);

      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      let response;
      const apiUrl = editingProduct ? `${API}/products/${editingProduct.id}` : `${API}/products`;
      const method = editingProduct ? 'PUT' : 'POST';
      
      console.log(`📡 Haciendo ${method} a: ${apiUrl}`);
      console.log(`📝 Producto en edición:`, editingProduct);
      
      if (editingProduct) {
        // Update existing product
        console.log(`Updating product ${editingProduct.id}...`);
        response = await axios.put(apiUrl, productData, { headers });
        
        // Update in products list correctly
        const updatedProducts = products.map(p => {
          if (p.id === editingProduct.id) {
            console.log(`✅ Actualizando producto en lista:`, response.data);
            return response.data;
          }
          return p;
        });
        setProducts(updatedProducts);
        alert('✅ Producto actualizado correctamente');
        console.log('Product updated:', response.data);
      } else {
        // Create new product
        console.log('Creating new product...');
        response = await axios.post(apiUrl, productData, { headers });
        // Add to products list
        setProducts([...products, response.data]);
        alert('✅ Producto creado correctamente');
        console.log('Product created:', response.data);
      }

      resetForm();
      onClose();

      // Recargar productos para asegurar sincronización
      setTimeout(async () => {
        try {
          const refreshResponse = await axios.get(`${API}/products?limit=1000`);
          setProducts(refreshResponse.data);
          console.log('🔄 Productos recargados:', refreshResponse.data.length);
        } catch (error) {
          console.error('Error recargando productos:', error);
        }
      }, 1000);

    } catch (error) {
      console.error('❌ ERROR COMPLETO:', error);
      console.error('❌ Response:', error.response?.data);
      console.error('❌ Status:', error.response?.status);
      
      if (error.response?.status === 401) {
        alert('❌ Error de autenticación. Reintentando...');
        localStorage.removeItem('adminToken');
      } else if (error.response?.data?.detail) {
        const detail = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
        alert(`❌ Error del servidor: ${detail}`);
      } else {
        alert(`❌ Error: ${error.message || 'Error desconocido'}`);
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

  // Mostrar login de manager si no está autenticado
  if (showManagerLogin && !isManagerAuthenticated) {
    return (
      <div className="admin-panel-overlay">
        <div className="admin-panel">
          <div className="admin-header">
            <h2>🔐 Acceso de Manager - HANNU CLOTHES</h2>
            <button className="admin-close" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
          
          <div className="admin-content">
            {!showPasswordRecovery ? (
            <div className="manager-login-form">
              <h3>Autenticación Requerida</h3>
              <p>Solo usuarios autorizados pueden acceder al panel de administración del catálogo.</p>
              
              <div className="form-group">
                <label>Usuario Manager</label>
                <input
                  type="text"
                  value={managerCredentials.username}
                  onChange={(e) => setManagerCredentials({
                    ...managerCredentials, 
                    username: e.target.value
                  })}
                  placeholder="Ingresa tu usuario"
                  onKeyPress={(e) => e.key === 'Enter' && authenticateManager()}
                />
              </div>
              
              <div className="form-group">
                <label>Contraseña</label>
                <input
                  type="password"
                  value={managerCredentials.password}
                  onChange={(e) => setManagerCredentials({
                    ...managerCredentials, 
                    password: e.target.value
                  })}
                  placeholder="Ingresa tu contraseña"
                  onKeyPress={(e) => e.key === 'Enter' && authenticateManager()}
                />
              </div>
              
              <div className="form-actions">
                <button 
                  className="save-btn" 
                  onClick={authenticateManager}
                  disabled={!managerCredentials.username || !managerCredentials.password}
                >
                  <User size={16} />
                  Acceder al Panel
                </button>
                <button className="cancel-btn" onClick={onClose}>
                  Cancelar
                </button>
              </div>
              
              <div className="recovery-section">
                <button 
                  className="recovery-link"
                  onClick={() => setShowPasswordRecovery(true)}
                >
                  ¿Olvidaste tu contraseña?
                </button>
              </div>
              
              <div className="manager-info">
                <small>Contacta al administrador del sistema si no tienes credenciales de acceso.</small>
              </div>
            </div>
            ) : (
            <div className="password-recovery-form">
              <h3>Recuperar Contraseña</h3>
              <p>Ingresa tu email autorizado para recibir las credenciales de acceso.</p>
              
              <div className="form-group">
                <label>Email Autorizado</label>
                <input
                  type="email"
                  value={recoveryEmail}
                  onChange={(e) => setRecoveryEmail(e.target.value)}
                  placeholder="Ingresa tu email"
                  onKeyPress={(e) => e.key === 'Enter' && handlePasswordRecovery()}
                />
              </div>
              
              <div className="form-actions">
                <button 
                  className="save-btn" 
                  onClick={handlePasswordRecovery}
                  disabled={!recoveryEmail}
                >
                  📧 Enviar Credenciales
                </button>
                <button 
                  className="cancel-btn" 
                  onClick={() => {
                    setShowPasswordRecovery(false);
                    setRecoveryEmail('');
                  }}
                >
                  Volver al Login
                </button>
              </div>
              
              <div className="manager-info">
                <small>Solo emails autorizados pueden recuperar credenciales de acceso.</small>
              </div>
            </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-panel-overlay">
      <div className="admin-panel">
        <div className="admin-header">
          <h2>Panel de Administración - HANNU CLOTHES</h2>
          <div className="admin-header-actions">
            <span className="manager-status">
              👤 Manager: {localStorage.getItem('managerUsername') || 'Autorizado'}
            </span>
            <button 
              className="mass-upload-btn" 
              onClick={() => setShowMassUpload(!showMassUpload)}
              title="Carga masiva de imágenes"
            >
              📸 Carga Masiva
            </button>
            <button className="logout-btn" onClick={logoutManager} title="Cerrar sesión">
              <User size={16} />
              Salir
            </button>
            <button className="admin-close" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
        </div>
        
        {showMassUpload && (
          <div className="mass-upload-section">
            <div className="mass-upload-header">
              <h3>🚀 Carga Masiva de Imágenes - Llegar al 100%</h3>
              <p>Sube las imágenes de los productos que no tienen imágenes funcionando</p>
            </div>

            <div className="missing-products-info">
              <h4>📋 Productos que necesitan imágenes ({missingImageProducts.length}):</h4>
              <div className="missing-products-list">
                {missingImageProducts.map((product, i) => (
                  <span key={i} className="missing-product-tag">{product}</span>
                ))}
              </div>
            </div>

            <div className="file-upload-area">
              <label className="file-upload-label">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelection}
                  style={{display: 'none'}}
                />
                📁 Seleccionar Imágenes
              </label>
              <p>Selecciona las imágenes desde tu computador</p>
            </div>

            {massUploadFiles.length > 0 && (
              <div className="files-mapping">
                <h4>Asigna cada imagen a su producto:</h4>
                <div className="files-grid">
                  {massUploadFiles.map((fileData, index) => (
                    <div key={index} className="file-item">
                      <img 
                        src={fileData.preview} 
                        alt="Preview" 
                        className="file-preview"
                      />
                      <select 
                        value={fileData.productName}
                        onChange={(e) => updateProductName(index, e.target.value)}
                        className="product-select"
                      >
                        <option value="">Seleccionar producto</option>
                        {missingImageProducts.map(product => (
                          <option key={product} value={product}>{product}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>

                <div className="upload-actions">
                  <button 
                    className="upload-all-btn"
                    onClick={handleMassUpload}
                    disabled={saving || massUploadFiles.some(f => !f.productName)}
                  >
                    {saving ? '🔄 Subiendo...' : `🚀 Subir ${massUploadFiles.length} Imágenes`}
                  </button>
                  
                  {uploadProgress && (
                    <div className="upload-progress">
                      Subiendo: {uploadProgress.current}/{uploadProgress.total}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

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
                  <option value="blusas">Tops & Bodys</option>
                  <option value="faldas">Faldas & Pantalones</option>
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
                <input
                  type="text"
                  value={formData.colors}
                  onChange={(e) => setFormData({...formData, colors: e.target.value})}
                  placeholder="Ej: Rosa, Azul, Negro (separados por comas)"
                />
              </div>
              
              <div className="form-group full-width">
                <label>Tallas Disponibles</label>
                <input
                  type="text"
                  value={formData.sizes}
                  onChange={(e) => setFormData({...formData, sizes: e.target.value})}
                  placeholder="Ej: XS, S, M, L, XL (separados por comas)"
                />
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
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    // Load products from backend
    const loadProducts = async () => {
      try {
        setLoading(true);
        // Cargar TODOS los productos sin límite
        const response = await axios.get(`${API}/products?limit=1000`);
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

  const filteredProducts = products.filter(product => {
    const matchesCategory = selectedCategory === 'todos' || product.category === selectedCategory;
    const matchesSearch = searchQuery === '' || 
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (product.colors && product.colors.some(color => 
        color.toLowerCase().includes(searchQuery.toLowerCase())
      ));
    return matchesCategory && matchesSearch;
  });

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
        // Asegurar autenticación antes de eliminar
        let token = localStorage.getItem('adminToken');
        if (!token) {
          console.log('No hay token, obteniendo nuevo token...');
          token = await loginAdmin();
          if (!token) {
            alert('❌ Error: No se pudo obtener autenticación de administrador');
            return;
          }
        }

        const headers = {
          'Authorization': `Bearer ${token}`
        };

        console.log(`🗑️ Eliminando producto: ${productId}`);
        await axios.delete(`${API}/products/${productId}`, { headers });
        
        // Actualizar lista local inmediatamente
        const updatedProducts = products.filter(p => p.id !== productId);
        setProducts(updatedProducts);
        
        alert('✅ Producto eliminado correctamente');
        
        // Recargar para confirmar sincronización
        setTimeout(async () => {
          try {
            const refreshResponse = await axios.get(`${API}/products?limit=1000`);
            setProducts(refreshResponse.data);
            console.log('🔄 Lista actualizada después de eliminación');
          } catch (error) {
            console.error('Error recargando después de eliminar:', error);
          }
        }, 500);
        
      } catch (error) {
        console.error('Error deleting product:', error);
        if (error.response?.status === 401) {
          alert('❌ Error: Sesión de administrador expirada. Reintentando...');
          localStorage.removeItem('adminToken');
          // Reintentar con nueva autenticación
          const newToken = await loginAdmin();
          if (newToken) {
            handleDeleteProduct(productId); // Reintentar
          }
        } else {
          alert(`❌ Error al eliminar el producto: ${error.response?.data?.detail || error.message}`);
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
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        showSearch={showSearch}
        setShowSearch={setShowSearch}
      />
      
      <main>
        <Hero />
        
        <section id="catalog-section" className="products catalog">
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
        
        <section className="immediate-delivery">
          <div className="container">
            <div className="delivery-content">
              <div className="delivery-icons">
                <img src="https://customer-assets.emergentagent.com/job_style-showcase-27/artifacts/w75ccsee_image.png" alt="Entrega inmediata" className="delivery-icon" />
                <img src="https://customer-assets.emergentagent.com/job_style-showcase-27/artifacts/w75ccsee_image.png" alt="Entrega inmediata" className="delivery-icon" />
              </div>
              <div className="delivery-text">
                <h3>📦 Entrega Inmediata 💖</h3>
                <p>LAS PRENDAS PARA ENTREGA INMEDIATA ESTÁN EN NUESTRAS 2 HISTORIAS DESTACADAS DE INSTAGRAM</p>
                <a href="https://instagram.com/hannuclothes" target="_blank" rel="noopener noreferrer" className="instagram-link">
                  <Instagram size={20} />
                  @hannuclothes
                </a>
              </div>
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
            <h2>Políticas Hannu</h2>
            <div className="policies-grid">
              
              <div className="policy-card">
                <h3>🪡 Confeccionamos Modelos Específicos</h3>
                <p>
                  Se pueden realizar bajo pedido modelos específicos y/o prendas que no estén disponibles para entrega inmediata con un tiempo de realización de 4 a 8 días hábiles.
                </p>
              </div>

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
                <li>Tops & Bodys</li>
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