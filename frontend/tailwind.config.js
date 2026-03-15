/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6fff9',
          100: '#b3fff0',
          200: '#80ffe6',
          300: '#4dffdd',
          400: '#1affd3',
          500: '#00D9A3',
          600: '#00b386',
          700: '#008c69',
          800: '#00664c',
          900: '#004030',
        },
        secondary: {
          50: '#e6f2f5',
          100: '#b3d9e3',
          200: '#80c0d1',
          300: '#4da7bf',
          400: '#1a8ead',
          500: '#1A4D5C',
          600: '#154149',
          700: '#103436',
          800: '#0b2723',
          900: '#061a10',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
