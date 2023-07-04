module.exports = {
  content: [
    "./src/**/*.{html,py,js}",
  ],
  media: false,
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "rgb(var(--color-primary-50) / <alpha-value>)",
          100: "rgb(var(--color-primary-100) / <alpha-value>)",
          200: "rgb(var(--color-primary-200) / <alpha-value>)",
          300: "rgb(var(--color-primary-300) / <alpha-value>)",
          400: "rgb(var(--color-primary-400) / <alpha-value>)",
          500: "rgb(var(--color-primary-500) / <alpha-value>)",
          600: "rgb(var(--color-primary-600) / <alpha-value>)",
          700: "rgb(var(--color-primary-700) / <alpha-value>)",
          800: "rgb(var(--color-primary-800) / <alpha-value>)",
          900: "rgb(var(--color-primary-900) / <alpha-value>)"
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
        "4.5": "1.125rem",
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
  plugins: [
      require('@tailwindcss/typography'),
  ]
}
