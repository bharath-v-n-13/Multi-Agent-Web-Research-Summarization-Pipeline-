/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Theme Colors matching premium minimalistic look
        primary: {
          50: "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          400: "#94A3B8",
          500: "#64748B",
          600: "#475569",
          700: "#334155",
          800: "#1E293B",
          900: "#0F172A",
          950: "#020617",
        },
        brand: {
          navy: "#002B49",
          teal: "#008080",
          accent: "#3B82F6",
        }
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      boxShadow: {
        soft: "0 2px 12px 0 rgba(0, 0, 0, 0.05)",
        premium: "0 8px 30px 0 rgba(0, 0, 0, 0.08)",
      }
    },
  },
  plugins: [],
}
