import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#e8edf5",
          100: "#c5d0e6",
          200: "#9fb0d4",
          300: "#7890c2",
          400: "#5a77b5",
          500: "#3c5ea8",
          600: "#2d4d96",
          700: "#1e3a7e",
          800: "#122866",
          900: "#0A1628",
          950: "#060e1a",
        },
        electric: {
          50: "#eff6ff",
          100: "#dbeafe",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563EB",
          700: "#1d4ed8",
        },
      },
      fontFamily: {
        sans: ["DM Sans", "system-ui", "sans-serif"],
        serif: ["DM Serif Display", "Georgia", "serif"],
      },
      animation: {
        "bounce-dot": "bounceDot 1.2s infinite ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "fade-in": "fadeIn 0.2s ease-out",
      },
      keyframes: {
        bounceDot: {
          "0%, 80%, 100%": { transform: "scale(0)", opacity: "0.3" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
        slideUp: {
          from: { transform: "translateY(20px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
