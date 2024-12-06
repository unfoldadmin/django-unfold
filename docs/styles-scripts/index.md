---
title: Styles & scripts
order: 8
description: Custom styles and scripts for Unfold.
---

# Adding custom styles and scripts

To add new custom styles, for example for custom dashboard, it is possible to load them via **STYLES** key in **UNFOLD** dict. This key accepts a list of strings or lambda functions which will be loaded on all pages. JavaScript files can be loaded by using similar apprach, but **SCRIPTS** is used.

```python
# settings.py

from django.templatetags.static import static

UNFOLD = {
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/scripts.js"),
    ],
}
```

## Project level Tailwind stylesheet

When creating custom dashboard or adding custom components, it is needed to add own styles. Adding custom styles is described above. Most of the time, it is supposed that new elements are going to match with the rest of the administration panel. First of all, create tailwind.config.js in your application. Below is located minimal configuration for this file.

```javascript
// tailwind.config.js

module.exports = {
  // Support dark mode classes
  darkMode: "class",
  // Your projects files to look for Tailwind classes
  content: ["./your_project/**/*.{html,py,js}"],
  //
  // In case custom colors are defined in UNFOLD["COLORS"]
  colors: {
    font: {
      "subtle-light": "rgb(var(--color-font-subtle-light) / <alpha-value>)",
      "subtle-dark": "rgb(var(--color-font-subtle-dark) / <alpha-value>)",
      "default-light": "rgb(var(--color-font-default-light) / <alpha-value>)",
      "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
      "important-light": "rgb(var(--color-font-important-light) / <alpha-value>)",
      "important-dark": "rgb(var(--color-font-important-dark) / <alpha-value>)",
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
  },
};
```


```css
/* styles.css */

@tailwind base;
@tailwind components;
@tailwind utilities;
```

Once the configuration file is set, it is possible to compile new styles which can be loaded into admin by using **STYLES** key in **UNFOLD** dict.

```bash
npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify
```
