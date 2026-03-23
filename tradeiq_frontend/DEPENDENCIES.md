/**
 * TradeIQ Frontend - Package Configuration
 * 
 * This file contains all npm dependencies for the React + Vite frontend.
 * 
 * Install all dependencies:
 * npm install
 * 
 * Start development server:
 * npm run dev
 * 
 * Build for production:
 * npm run build
 */

{
  "name": "tradeiq_frontend",
  "version": "1.0.0",
  "description": "TradeIQ - Stock Market Prediction Frontend",
  "author": "TradeIQ Team",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src/ --ext js,jsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.54.0",
    "eslint-plugin-react": "^7.33.2"
  },
  "keywords": [
    "stock",
    "prediction",
    "machine learning",
    "react",
    "django",
    "finance"
  ]
}
