module.exports = {
  content: [
    "./src/**/*.{html,py,js}",
  ],
  media: false,
  theme: {
    extend: {
      colors: {
        primary: {
          100: 'var(--color-primary-100)',
          200: 'var(--color-primary-200)',
          300: 'var(--color-primary-300)',
          400: 'var(--color-primary-400)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
          700: 'var(--color-primary-700)',
          800: 'var(--color-primary-800)',
          900: 'var(--color-primary-900)'
        }
      },
      fontSize: {
        0: [0, 1],
        xxs: ["11px", "14px"],
      },
      fontFamily: {
        sans: ["Inter",  "sans-serif"]
      },
      height: {
        "9.5": "2.375rem",
      },
      minWidth: {
        "sidebar": "18rem",
      },
      spacing: {
        "68": "17rem",
        "128": "32rem",
      },
      transitionProperty: {
        "height": "height",
        "width": "width",
      },
      width: {
        "9.5": "2.375rem",
        "sidebar": "18rem",
      },
    },
  },
  variants: {
    extend: {
      borderColor: ["checked", "focus-within", "hover"],
      display: ["group-hover"],
      overflow: ["hover"],
      textColor: ["hover"]
    }
  },
  plugins: []
}
