module.exports = {
  content: ["./src/**/*.{html,py,js}"],
  media: false,
  darkMode: "class",
  theme: {
    extend: {
      borderRadius: {
        DEFAULT: "var(--border-radius, 6px)",
      },
      colors: {
        base: {
          50: "rgb(var(--color-base-50) / <alpha-value>)",
          100: "rgb(var(--color-base-100) / <alpha-value>)",
          200: "rgb(var(--color-base-200) / <alpha-value>)",
          300: "rgb(var(--color-base-300) / <alpha-value>)",
          400: "rgb(var(--color-base-400) / <alpha-value>)",
          500: "rgb(var(--color-base-500) / <alpha-value>)",
          600: "rgb(var(--color-base-600) / <alpha-value>)",
          700: "rgb(var(--color-base-700) / <alpha-value>)",
          800: "rgb(var(--color-base-800) / <alpha-value>)",
          900: "rgb(var(--color-base-900) / <alpha-value>)",
          950: "rgb(var(--color-base-950) / <alpha-value>)",
        },
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
          900: "rgb(var(--color-primary-900) / <alpha-value>)",
          950: "rgb(var(--color-primary-950) / <alpha-value>)",
        },
        font: {
          "subtle-light": "rgb(var(--color-font-subtle-light) / <alpha-value>)",
          "subtle-dark": "rgb(var(--color-font-subtle-dark) / <alpha-value>)",
          "default-light":
            "rgb(var(--color-font-default-light) / <alpha-value>)",
          "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
          "important-light":
            "rgb(var(--color-font-important-light) / <alpha-value>)",
          "important-dark":
            "rgb(var(--color-font-important-dark) / <alpha-value>)",
        },
      },
      fontSize: {
        0: [0, 1],
        xxs: ["11px", "14px"],
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      height: {
        4.5: "1.125rem",
        9.5: "2.375rem",
      },
      minHeight: {
        9.5: "2.375rem",
      },
      minWidth: {
        sidebar: "18rem",
      },
      spacing: {
        68: "17rem",
        128: "32rem",
      },
      transitionProperty: {
        height: "height",
        width: "width",
      },
      width: {
        4.5: "1.125rem",
        9.5: "2.375rem",
        sidebar: "18rem",
      },
    },
  },
  variants: {
    extend: {
      borderColor: ["checked", "focus-within", "hover"],
      display: ["group-hover"],
      overflow: ["hover"],
      textColor: ["hover"],
    },
  },
  plugins: [require("@tailwindcss/typography")],
  safelist: [
    "border-2",
    "border-base-300",
    "border-base-400",
    "dark:border-base-500",
    "border-l",
    "border-b-0",
    "border-l-0",
    "border-r-0",
    "border-t-0",
    "flex-grow",
    "pb-0",
    "tracking-normal",
    "h-3",
    "w-3",
    "w-96",
    "max-w-96",
    "md:border-0",
    "md:border-r",
    "md:w-48",
    {
      pattern: /col-span-+/,
      variants: ["md", "lg"],
    },
    {
      pattern: /grid-cols-+/,
      variants: ["md", "lg"],
    },
    {
      pattern: /gap-+/,
      variants: ["md", "lg"],
    },
    {
      pattern: /bg-(primary)-(50|100|200|300|400|500|600|700|800|900|950)/,
      variants: ["dark"],
    },
    {
      pattern: /w-(1\/2|1\/3|2\/3|1\/4|2\/4|3\/4|1\/5|2\/5|3\/5|4\/5)/,
      variants: ["md", "lg"],
    },
  ],
};
