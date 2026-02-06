/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // BLOOM Design System
        'bloom-bg': '#ffffff',
        'bloom-bg-subtle': '#f8f8f8',
        'bloom-black': '#1a1a1a',
        'bloom-gray': '#e5e5e5',
        'bloom-gray-dark': '#999999',
        'bloom-yellow': '#f5c542',
        'bloom-orange': '#e85a3c',
        'bloom-green': '#22c55e',
        'bloom-text': '#1a1a1a',
        'bloom-text-dim': '#888888',
      },
      fontFamily: {
        'inter': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderRadius: {
        'pill': '24px',
        'node': '50%',
      },
      spacing: {
        '18': '4.5rem',
        '76': '19rem',
      },
    },
  },
  plugins: [],
}
