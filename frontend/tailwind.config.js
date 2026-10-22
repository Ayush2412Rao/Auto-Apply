/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        jet: {
          DEFAULT: '#0A0A0A',
          50: '#1e1e1e',
          100: '#181818',
          200: '#141414',
          300: '#101010',
          surface: '#121215',
          card: '#151518',
          border: '#24242b',
        },
        cerulean: {
          DEFAULT: '#007BA7',
          50: '#e6f5fb',
          100: '#bce5f5',
          200: '#8ed2ef',
          300: '#5cbee8',
          400: '#2daee3',
          500: '#007BA7',
          600: '#006c93',
          700: '#005878',
          800: '#00455e',
          900: '#003347',
        },
        neon: {
          DEFAULT: '#FF2D95',
          50: '#ffe6f2',
          100: '#ffb3d9',
          200: '#ff80c0',
          300: '#ff4da6',
          400: '#ff2d95',
          500: '#FF2D95',
          600: '#e61e7e',
          700: '#cc1068',
          800: '#b30553',
          900: '#800038',
        },
        brand: {
          blue: '#007BA7',
          rose: '#FF2D95',
          dark: '#0A0A0A',
        }
      },
      boxShadow: {
        'cerulean': '0 0 25px -5px rgba(0, 123, 167, 0.45)',
        'neon': '0 0 25px -5px rgba(255, 45, 149, 0.45)',
        'dual': '0 0 30px -5px rgba(0, 123, 167, 0.35), 0 0 15px -3px rgba(255, 45, 149, 0.25)',
      }
    },
  },
  plugins: [],
}
