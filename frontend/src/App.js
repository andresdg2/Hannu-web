import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { ShoppingCart, User, Search, Menu, X, Heart, Star, ArrowRight, Check, Phone, Mail, MapPin } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sample product data (will be replaced with API data)
const sampleProducts = [
  {
    id: 1,
    name: "Elegant Rose Dress",
    price: 150000,
    category: "dresses",
    image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85",
    description: "Vestido elegante perfecto para ocasiones especiales. Confeccionado en tela de alta calidad.",
    composition: "95% Algodón, 5% Elastano",
    care: "Lavar a máquina en agua fría, no usar blanqueador",
    sizes: ["XS", "S", "M", "L", "XL"]
  },
  {
    id: 2,
    name: "Striped Essential Top",
    price: 75000,
    category: "tops",
    image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85",
    description: "Top de rayas clásico que combina con todo. Ideal para el día a día con un toque elegante.",
    composition: "100% Algodón orgánico",
    care: "Lavar a máquina en agua tibia, secar al aire",
    sizes: ["XS", "S", "M", "L", "XL"]
  },
  {
    id: 3,
    name: "Premium Denim",
    price: 120000,
    category: "bottoms",
    image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85",
    description: "Jeans de corte perfecto con acabado premium. Comodidad y estilo en una sola prenda.",
    composition: "82% Algodón, 16% Poliéster, 2% Elastano",
    care: "Lavar del revés en agua fría, no usar blanqueador",
    sizes: ["26", "28", "30", "32", "34", "36"]
  },
  {
    id: 4,
    name: "Leather Crossbody Bag",
    price: 95000,
    category: "accessories",
    image: "https://images.unsplash.com/photo-1559563458-527698bf5295?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGFjY2Vzc29yaWVzfGVufDB8fHx8MTc1Njk5OTY3Mnww&ixlib=rb-4.1.0&q=85",
    description: "Bolso cruzado de cuero genuino con diseño minimalista. El accesorio perfecto para cualquier outfit.",
    composition: "100% Cuero genuino, forro de algodón",
    care: "Limpiar con paño húmedo, aplicar acondicionador de cuero ocasionalmente",
    sizes: ["Único"]
  }
];

const categories = [
  { id: "all", name: "Todo", image: null },
  { id: "dresses", name: "Vestidos", image: "https://images.unsplash.com/photo-1633077705107-8f53a004218f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMGRyZXNzZXN8ZW58MHx8fHwxNzU2OTk5NjU1fDA&ixlib=rb-4.1.0&q=85" },
  { id: "tops", name: "Blusas", image: "https://images.unsplash.com/photo-1530981785497-a62037228fe9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHx3b21lbiUyMHRvcHN8ZW58MHx8fHwxNzU2OTk5NjYwfDA&ixlib=rb-4.1.0&q=85" },
  { id: "bottoms", name: "Pantalones", image: "https://images.unsplash.com/photo-1597544004999-11b0390e0cc5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGJvdHRvbXN8ZW58MHx8fHwxNzU2OTk5NjY2fDA&ixlib=rb-4.1.0&q=85" },
  { id: "accessories", name: "Accesorios", image: "https://images.unsplash.com/photo-1559563458-527698bf5295?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzB8MHwxfHNlYXJjaHwxfHx3b21lbiUyMGFjY2Vzc29yaWVzfGVufDB8fHx8MTc1Njk5OTY3Mnww&ixlib=rb-4.1.0&q=85" }
];

const Header = ({ cart, toggleCart, selectedCategory, setSelectedCategory }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const cartItemsCount = cart.reduce((total, item) => total + item.quantity, 0);

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <img src="https://customer-assets.emergentagent.com/job_7ac0f3ca-81b2-49ce-a27b-bd65357f766a/artifacts/d670l3hu_Logo%20Hannu%20Clothes.jpeg" alt="HANNU CLOTHES" />
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
            <button className="action-btn" onClick={toggleCart}>
              <ShoppingCart size={20} />
              {cartItemsCount > 0 && <span className="cart-badge">{cartItemsCount}</span>}
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
          <h1>Elegancia<br />Femenina</h1>
          <p>Descubre nuestra colección exclusiva de prendas diseñadas para la mujer moderna que valora la elegancia y la calidad.</p>
          <button className="cta-button">
            Explorar Colección
            <ArrowRight size={20} />
          </button>
        </div>
        <div className="hero-image">
          <img src="https://images.unsplash.com/photo-1678637803384-947954f11c10?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxlbGVnYW50JTIwd29tZW4lMjBmYXNoaW9ufGVufDB8fHx8MTc1Njk5OTYxOHww&ixlib=rb-4.1.0&q=85" alt="Elegant Fashion" />
        </div>
      </div>
    </section>
  );
};

const ProductCard = ({ product, onAddToCart }) => {
  const [isLiked, setIsLiked] = useState(false);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.image} alt={product.name} />
        <button 
          className={`wishlist-btn ${isLiked ? 'liked' : ''}`}
          onClick={() => setIsLiked(!isLiked)}
        >
          <Heart size={18} fill={isLiked ? 'currentColor' : 'none'} />
        </button>
      </div>
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="product-price">{formatPrice(product.price)}</p>
        <div className="product-actions">
          <button 
            className="add-to-cart-btn"
            onClick={() => onAddToCart(product)}
          >
            Añadir al Carrito
          </button>
        </div>
      </div>
    </div>
  );
};

const ProductModal = ({ product, isOpen, onClose, onAddToCart }) => {
  const [selectedSize, setSelectedSize] = useState('');

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (!isOpen || !product) return null;

  const handleAddToCart = () => {
    if (selectedSize) {
      onAddToCart({...product, selectedSize});
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="product-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-content">
          <div className="modal-image">
            <img src={product.image} alt={product.name} />
          </div>
          
          <div className="modal-info">
            <h2>{product.name}</h2>
            <p className="modal-price">{formatPrice(product.price)}</p>
            <p className="product-description">{product.description}</p>
            
            <div className="product-details">
              <div className="detail-section">
                <h4>Composición</h4>
                <p>{product.composition}</p>
              </div>
              
              <div className="detail-section">
                <h4>Cuidados</h4>
                <p>{product.care}</p>
              </div>
              
              <div className="detail-section">
                <h4>Talla</h4>
                <div className="size-selector">
                  {product.sizes.map(size => (
                    <button
                      key={size}
                      className={`size-btn ${selectedSize === size ? 'selected' : ''}`}
                      onClick={() => setSelectedSize(size)}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <button 
              className="add-to-cart-btn large"
              onClick={handleAddToCart}
              disabled={!selectedSize}
            >
              Añadir al Carrito - {formatPrice(product.price)}
            </button>
            
            <div className="shipping-info">
              <div className="shipping-item">
                <Check size={16} />
                <span>Envío gratis en compras superiores a $150.000</span>
              </div>
              <div className="shipping-item">
                <Check size={16} />
                <span>Cambios y devoluciones hasta 30 días</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Cart = ({ cart, isOpen, onClose, onUpdateQuantity, onRemoveItem }) => {
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (!isOpen) return null;

  return (
    <div className="cart-overlay" onClick={onClose}>
      <div className="cart-sidebar" onClick={e => e.stopPropagation()}>
        <div className="cart-header">
          <h3>Carrito de Compras</h3>
          <button className="cart-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        
        <div className="cart-items">
          {cart.length === 0 ? (
            <div className="empty-cart">
              <ShoppingCart size={48} />
              <p>Tu carrito está vacío</p>
            </div>
          ) : (
            cart.map(item => (
              <div key={`${item.id}-${item.selectedSize}`} className="cart-item">
                <img src={item.image} alt={item.name} />
                <div className="cart-item-info">
                  <h4>{item.name}</h4>
                  <p>Talla: {item.selectedSize}</p>
                  <p className="cart-item-price">{formatPrice(item.price)}</p>
                  <div className="quantity-controls">
                    <button onClick={() => onUpdateQuantity(item.id, item.selectedSize, item.quantity - 1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => onUpdateQuantity(item.id, item.selectedSize, item.quantity + 1)}>+</button>
                  </div>
                </div>
                <button 
                  className="remove-item"
                  onClick={() => onRemoveItem(item.id, item.selectedSize)}
                >
                  <X size={16} />
                </button>
              </div>
            ))
          )}
        </div>
        
        {cart.length > 0 && (
          <div className="cart-footer">
            <div className="cart-total">
              <strong>Total: {formatPrice(total)}</strong>
            </div>
            <button className="checkout-btn">
              Proceder al Pago
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const About = () => {
  return (
    <section className="about">
      <div className="container">
        <div className="about-content">
          <div className="about-text">
            <h2>Nuestra Historia</h2>
            <p>
              HANNU CLOTHES nace del amor por la moda femenina y la pasión por crear prendas que realcen la belleza natural de cada mujer. 
              Cada pieza es cuidadosamente seleccionada pensando en la mujer moderna que valora la calidad, el estilo y la comodidad.
            </p>
            <p>
              Creemos que la ropa es una forma de expresión personal, y por eso ofrecemos una colección diversa que se adapta a diferentes 
              momentos y estilos de vida, siempre manteniendo la elegancia como nuestro sello distintivo.
            </p>
          </div>
          <div className="about-image">
            <img src="https://images.pexels.com/photos/33751207/pexels-photo-33751207.jpeg" alt="Our Story" />
          </div>
        </div>
      </div>
    </section>
  );
};

const Testimonials = () => {
  const testimonials = [
    {
      name: "María González",
      text: "La calidad de las prendas es excepcional. Mi vestido HANNU se ha convertido en mi favorito para ocasiones especiales.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1553984658-d17e19aa281a"
    },
    {
      name: "Andrea Rodríguez", 
      text: "Excelente servicio al cliente y prendas hermosas. Definitivamente volveré a comprar.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1553984658-d17e19aa281a"
    },
    {
      name: "Carolina Martínez",
      text: "Me encanta la elegancia y feminidad de cada pieza. HANNU CLOTHES entiende perfectamente el estilo femenino.",
      rating: 5,
      image: "https://images.unsplash.com/photo-1553984658-d17e19aa281a"
    }
  ];

  return (
    <section className="testimonials">
      <div className="container">
        <h2>Lo que Dicen Nuestras Clientas</h2>
        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="testimonial-card">
              <div className="stars">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} size={16} fill="currentColor" />
                ))}
              </div>
              <p>"{testimonial.text}"</p>
              <div className="testimonial-author">
                <img src={testimonial.image} alt={testimonial.name} />
                <span>{testimonial.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h4>HANNU CLOTHES</h4>
            <p>Elegancia y estilo para la mujer moderna.</p>
            <div className="footer-logo">
              <img src="https://customer-assets.emergentagent.com/job_7ac0f3ca-81b2-49ce-a27b-bd65357f766a/artifacts/d670l3hu_Logo%20Hannu%20Clothes.jpeg" alt="HANNU CLOTHES" />
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Información</h4>
            <ul>
              <li><a href="#shipping">Envíos</a></li>
              <li><a href="#returns">Cambios y Devoluciones</a></li>
              <li><a href="#size-guide">Guía de Tallas</a></li>
              <li><a href="#care">Cuidado de Prendas</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Políticas</h4>
            <ul>
              <li><a href="#shipping-policy">Política de Envíos</a></li>
              <li><a href="#return-policy">Política de Cambios</a></li>
              <li><a href="#privacy">Privacidad</a></li>
              <li><a href="#terms">Términos y Condiciones</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Contacto</h4>
            <div className="contact-info">
              <div className="contact-item">
                <Phone size={16} />
                <span>+57 300 123 4567</span>
              </div>
              <div className="contact-item">
                <Mail size={16} />
                <span>info@hannuclothes.com</span>
              </div>
              <div className="contact-item">
                <MapPin size={16} />
                <span>Bogotá, Colombia</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2024 HANNU CLOTHES. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  );
};

const Home = () => {
  const [products, setProducts] = useState(sampleProducts);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);

  useEffect(() => {
    // Test backend connection
    const testApi = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log('Backend connected:', response.data.message);
      } catch (e) {
        console.error('Backend connection failed:', e);
      }
    };
    testApi();
  }, []);

  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(product => product.category === selectedCategory);

  const addToCart = (product) => {
    const existingItem = cart.find(item => 
      item.id === product.id && item.selectedSize === product.selectedSize
    );
    
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id && item.selectedSize === product.selectedSize
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const updateQuantity = (id, size, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(id, size);
      return;
    }
    
    setCart(cart.map(item =>
      item.id === id && item.selectedSize === size
        ? { ...item, quantity: newQuantity }
        : item
    ));
  };

  const removeFromCart = (id, size) => {
    setCart(cart.filter(item => 
      !(item.id === id && item.selectedSize === size)
    ));
  };

  const openProductModal = (product) => {
    setSelectedProduct(product);
    setIsProductModalOpen(true);
  };

  return (
    <div className="app">
      <Header 
        cart={cart}
        toggleCart={() => setIsCartOpen(!isCartOpen)}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
      />
      
      <main>
        <Hero />
        
        <section className="products">
          <div className="container">
            <h2>Nuestra Colección</h2>
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
              {filteredProducts.map(product => (
                <div key={product.id} onClick={() => openProductModal(product)}>
                  <ProductCard
                    product={product}
                    onAddToCart={addToCart}
                  />
                </div>
              ))}
            </div>
          </div>
        </section>
        
        <About />
        <Testimonials />
      </main>
      
      <Footer />
      
      <Cart
        cart={cart}
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        onUpdateQuantity={updateQuantity}
        onRemoveItem={removeFromCart}
      />
      
      <ProductModal
        product={selectedProduct}
        isOpen={isProductModalOpen}
        onClose={() => setIsProductModalOpen(false)}
        onAddToCart={addToCart}
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