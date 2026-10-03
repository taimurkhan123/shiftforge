

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#0a0a0f",
          surface: "#12121a",
          elevated: "#1a1a24",
        },
        border: {
          subtle: "#22222e",
          DEFAULT: "#2a2a36",
        },
        text: {
          primary: "#e8e8f0",
          secondary: "#a0a0b0",
          muted: "#606070",
        },
        accent: {
          DEFAULT: "#6366f1",
          hover: "#818cf8",
          glow: "#4f46e5",
        },
        status: {
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          info: "#3b82f6",
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(99, 102, 241, 0.5)",
      },
    },
  },
  plugins: [],
}