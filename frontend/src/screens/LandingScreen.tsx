import React from "react";
import { colors, font } from "../style/theme";
import { IconHome, IconMenu, IconSparkle, IconArrowRight } from "../components/Icons";

interface LandingScreenProps {
  onEnter: () => void;
}

export function LandingScreen({ onEnter }: LandingScreenProps) {
  return (
    <div style={styles.root}>

      {/* Header */}
      <header style={styles.header}>
        <div style={{ color: colors.red }}>
          <IconHome />
        </div>
        <IconMenu />
      </header>

      {/* Foto do edifício + formas decorativas */}
      <div style={styles.buildingSection}>
        <img
          src="/src/assets/p.jpg"
          alt="Edifício moderno"
          style={styles.buildingImg}
        />
        <div style={styles.imageFade} />
      </div>

      {/* Conteúdo inferior esquerdo */}
      <div style={styles.bottomContent}>
        <div>
          <h1 style={styles.heroTitle}>HOME<br />MATCH</h1>
          <div style={styles.heroLine} />
        </div>

        <div style={styles.actions}>
          <p style={styles.heroSub}>
            uma nova solução<br />
            para o mercado<br />
            imobiliário
          </p>

          <button style={styles.ctaButton} onClick={onEnter}>
            Buscar imóvel
            <IconArrowRight size={18} />
          </button>

          <div style={styles.infoBadge}>
            ...
          </div>
        </div>
      </div>

    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    width: "100vw",
    height: "100vh",
    background: colors.bg,
    position: "relative",
    overflow: "hidden",
  },

  header: {
    position: "relative",
    zIndex: 10,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "20px 28px",
  },

  // Foto + formas
  buildingSection: {
    position: "absolute",
    top: 64,        // espaço para o header
    right: 0,
    width: "35vw",
    height: "calc(100vh - 64px)",
  },
  imageFade: {
    position: "absolute",
    inset: 0,
    zIndex: 2,
    boxShadow: "inset 20px 0 20px #F5F0EA, inset 0 20px 35px #F5F0EA",
  },

  blueCircle: {
    position: "absolute",
    top: "5%",
    right: "5%",
    width: "55%",
    paddingBottom: "55%",
    borderRadius: "50%",
    background: colors.navy,
  },
  buildingImg: {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    objectFit: "cover",
    objectPosition: "left center",

    borderRadius: 0,
  },

  redArc: {
    position: "absolute",
    bottom: "-10%",
    left: "-8%",
    width: "30%",
    paddingBottom: "30%",
    borderRadius: "50%",
    background: colors.red,
    zIndex: 2,
  },
  dotGrid: {
    position: "absolute",
    bottom: "12%",
    left: "4%",
    width: 64,
    height: 64,
    backgroundImage: `radial-gradient(circle, ${colors.red} 1.5px, transparent 1.5px)`,
    backgroundSize: "10px 10px",
    opacity: 0.6,
    zIndex: 3,
  },

  // Conteúdo inferior esquerdo
  bottomContent: {
    position: "absolute",
    top: 64,
    left: "5vw",
    zIndex: 10,
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
    gap: 2,

  },
  actions: {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    gap: 20,
  },
  heroTitle: {
    fontSize: "clamp(20px, 12vw, 200px)",
    fontWeight: 700,
    color: colors.red,
    margin: 0,
    lineHeight: 1.05,
    letterSpacing: "-1.5px",
    fontFamily: font.serif,
    textAlign: "center",
  },
  heroLine: {
    width: 44,
    height: 3,
    background: colors.red,
    margin: "12px 0",
  },
  heroSub: {
    fontSize: "clamp(14px, 1.4vw, 20px)",
    color: "#222",
    margin: 0,
    lineHeight: 1.5,
    fontStyle: "italic",
    fontFamily: font.serif,
  },

  ctaButton: {
    alignSelf: "flex-start",
    display: "flex",
    alignItems: "center",
    gap: 8,
    background: colors.red,
    color: colors.white,
    border: "none",
    borderRadius: 10,
    padding: "12px 20px",
    fontWeight: 700,
    fontSize: 14,
    cursor: "pointer",
    fontFamily: font.sans,
  },

  infoBadge: {
    background: colors.navy,
    color: colors.white,
    borderRadius: 10,
    width: "auto",
    minWidth: 160,
    padding: "12px 16px",

  },
  sparkles: {
    display: "flex",
    gap: 2,
    marginBottom: 6,
  },
  badgeText: {
    margin: 0,
    fontSize: 12,
    lineHeight: 1.6,
    fontFamily: font.sans,
  },
};