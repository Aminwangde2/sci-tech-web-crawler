/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'apple-bg': '#f5f5f7',
        'apple-text': '#1d1d1f',
        'apple-card': 'rgba(255, 255, 255, 0.7)',
      },
      boxShadow: {
        'apple': '0 4px 24px rgba(0, 0, 0, 0.04)',
      }
    },
  },
  plugins: [],
}