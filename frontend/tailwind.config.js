/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
        colors: {
            "primary": "#17cf54",
            "background-light": "#f6f8f6",
            "background-dark": "#112116",
            "surface-dark": "#1c261f",
            "surface-light": "#ffffff",
        },
        fontFamily: {
            "display": ["Manrope", "sans-serif"]
        },
    },
  },
  plugins: [],
}