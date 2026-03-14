/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './kkoala/templates/**/*.{html,js}',
    './kkoala/static/js/**/*.{js,ts}',
    './kkoala/components/**/*.{html,js}',
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
