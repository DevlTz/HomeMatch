import "./LandingScreen.css";

import heroBuilding from "../assets/predio.png";
import propertyPhoto from "../assets/p.jpg";

interface LandingScreenProps {
  onEnter: () => void;
}

const benefits = [
  {
    icon: "✦",
    title: "Busca inteligente",
    text: "Nossa IA entende suas preferencias e encontra imoveis ideais para voce.",
  },
  {
    icon: "⌖",
    title: "Imoveis verificados",
    text: "Opcoes analisadas com fotos, localizacao e detalhes completos.",
  },
  {
    icon: "♡",
    title: "Experiencia personalizada",
    text: "Recomendacoes sob medida com base no seu perfil e estilo de vida.",
  },
  {
    icon: "◇",
    title: "Transparencia total",
    text: "Informacoes claras para comparar e decidir com mais seguranca.",
  },
];

const properties = [
  {
    type: "Apartamento",
    title: "Apartamento moderno em Ponta Negra",
    location: "Ponta Negra, Natal - RN",
    stats: "2 quartos • 2 banheiros • 75 m²",
    price: "R$ 450.000",
  },
  {
    type: "Casa",
    title: "Casa com jardim e piscina no Capim Macio",
    location: "Capim Macio, Natal - RN",
    stats: "3 quartos • 3 banheiros • 180 m²",
    price: "R$ 720.000",
  },
  {
    type: "Apartamento",
    title: "Apartamento vista mar em Areia Preta",
    location: "Areia Preta, Natal - RN",
    stats: "3 quartos • 2 banheiros • 90 m²",
    price: "R$ 560.000",
  },
];

export function LandingScreen({ onEnter }: LandingScreenProps) {
  return (
    <main className="home-page">
      <header className="home-header">
        <a className="brand" href="/" aria-label="HomeMatch inicio">
          <span className="brand-mark" aria-hidden="true">
            <span />
          </span>
          <span>
            <strong>
              HOME<span>MATCH</span>
            </strong>
            <small>O imovel ideal para voce.</small>
          </span>
        </a>

        <nav className="main-nav" aria-label="Navegacao principal">
          <a className="active" href="#inicio">
            Inicio
          </a>
          <a href="#explorar">Explorar</a>
          <a href="#favoritos">Favoritos</a>
          <a href="#sobre">Sobre nos</a>
          <a href="#contato">Contato</a>
        </nav>

        <div className="header-actions">
          <button aria-label="Notificacoes" className="icon-button">
            ♫
            <span className="notification-dot">2</span>
          </button>
          <button aria-label="Favoritos" className="icon-button">
            ♡
          </button>
          <button className="profile-button">
            <span className="avatar">L</span>
            Ola, Lucas
            <span aria-hidden="true">⌄</span>
          </button>
        </div>
      </header>

      <section className="hero-section" id="inicio">
        <div className="hero-copy">
          <p className="eyebrow">HomeMatch IA</p>
          <h1>
            O imovel <span>ideal</span> para o seu momento de vida.
          </h1>
          <p className="hero-text">
            Nossa IA entende o que voce procura e encontra as melhores opcoes
            para morar, investir ou recomeçar.
          </p>

          <form className="ai-search" onSubmit={(event) => event.preventDefault()}>
            <span className="search-spark" aria-hidden="true">
              ✦
            </span>
            <label htmlFor="home-search" className="sr-only">
              Conte para nossa IA o que voce procura
            </label>
            <input
              id="home-search"
              placeholder="Conte para nossa IA o que voce procura..."
            />
            <button type="button" onClick={onEnter}>
              Buscar com IA
              <span aria-hidden="true">✦</span>
            </button>
          </form>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <div className="sky-glow" />
          <img src={heroBuilding} alt="" />
        </div>
      </section>

      <section className="benefits-panel" aria-label="Diferenciais">
        {benefits.map((benefit) => (
          <article className="benefit-card" key={benefit.title}>
            <span aria-hidden="true">{benefit.icon}</span>
            <div>
              <h2>{benefit.title}</h2>
              <p>{benefit.text}</p>
            </div>
          </article>
        ))}
      </section>

      <section className="suggestions" id="explorar">
        <div className="section-heading">
          <h2>
            Sugestoes <span>para voce</span>
          </h2>
          <a href="#explorar">Ver todas as opcoes →</a>
        </div>

        <div className="property-grid">
          {properties.map((property) => (
            <article className="property-card" key={property.title}>
              <div className="property-image">
                <img src={propertyPhoto} alt="" />
                <span>{property.type}</span>
                <button aria-label={`Favoritar ${property.title}`}>♡</button>
              </div>
              <div className="property-info">
                <h3>{property.title}</h3>
                <p>{property.location}</p>
                <small>{property.stats}</small>
                <div>
                  <strong>{property.price}</strong>
                  <a href="#detalhes">Ver detalhes →</a>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="app-banner">
        <div>
          <span className="phone-mockup" aria-hidden="true" />
          <div>
            <h2>Leve o HomeMatch com voce.</h2>
            <p>Baixe o app e tenha os melhores imoveis na palma da sua mao.</p>
          </div>
        </div>
        <div className="store-buttons">
          <button>App Store</button>
          <button>Google Play</button>
        </div>
      </section>
    </main>
  );
}
