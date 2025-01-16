---
title: Customizing Tailwind stylesheet
order: 1
description: How to customize Tailwind stylesheet to match Unfold design.
---

# Loading Tailwind stylesheet in Django project

When creating a custom dashboard or adding custom components, you may need to add your own styles to provide styling for new elements. The way styles can be loaded is described in the previous section. Once the styles are loaded, you can write CSS selectors with properties. This is sufficient if you don't need to use Tailwind.

Before starting with the Tailwind configuration at the project level, you need to install Tailwind CSS into your project by running `npm install tailwindcss` in the project directory. Don't forget to add `package.json` and `package-lock.json` to your repository.

Most likely, you'll want new elements to match the rest of the administration panel. First, create a `tailwind.config.js` file in your application. Below is the minimal configuration that contains color specifications so all Tailwind classes like `bg-primary-600` will match the admin theme.

```javascript
// tailwind.config.js

module.exports = {
  // Support dark mode classes
  darkMode: "class",
  // Your project's files to scan for Tailwind classes
  content: ["./your_project/**/*.{html,py,js}"],
  theme: {
    extend: {
      // Colors that match with UNFOLD["COLORS"] settings
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
          "default-light": "rgb(var(--color-font-default-light) / <alpha-value>)",
          "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
          "important-light": "rgb(var(--color-font-important-light) / <alpha-value>)",
          "important-dark": "rgb(var(--color-font-important-dark) / <alpha-value>)",
        }
      }
    }
  }
};
```

Next, create a `styles.css` file in your project's root directory. This file will be used to compile Tailwind CSS into your project:

```css
/* styles.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Your custom styles */
.some-class {
    @apply bg-primary-600;
}
```

Once the configuration file is set up, you can compile the styles which can be loaded into the admin using the **STYLES** key in the **UNFOLD** dictionary.

```bash
# One-time build with minified output
npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify

# Watch for changes and compile automatically with minified output
npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify --watch
```

You can automate this process by adding the following scripts to your `package.json` file:

```json
{
  "scripts": {
    "tailwind:watch": "npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify --watch",
    "tailwind:build": "npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify"
  }
  // rest of configuration
}
```
