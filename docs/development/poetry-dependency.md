---
title: Poetry dependecy path
order: 0
description: Learn how to set up pre-commit hooks, configure Poetry for development, and compile Tailwind CSS styles for Unfold theme development.
---

# Developing with changed Poetry path

The easiest way how to develop new features or fixes for Unfold is to directly implement them in existing project which you are working on. The prerequisite is to have django-unfold installed and the same time use Poetry for dependency management.

## Poetry configuration

To add a new feature or fix an issue, the easiest approach is to use django-unfold with Poetry. The process looks like this:

- Install django-unfold via `poetry add django-unfold`
- Clone the repository to your local computer
- Edit _pyproject.toml_ and update the django-unfold line to: `django-unfold = { path = "../django-unfold", develop = true}`
- Lock and update via `poetry lock && poetry update`

## Compiling Tailwind

The project contains a package.json with all dependencies required to compile the CSS file. The Tailwind configuration file is set to check all HTML, JS and Python files for Tailwind class occurrences. The prerequisite is to have Node.js installed on your computer.

```bash
# Install dependencies
npm install

# Manually run tailwindcss command
npx tailwindcss -i src/unfold/styles.css -o src/unfold/static/unfold/css/styles.css --watch --minify

# run after each change in code
npm run tailwind:watch
# run once
npm run tailwind:build
```

Some components like datepickers, calendars or selectors in the admin interface cannot be styled by overriding HTML templates, so their default styles are overridden in **styles.css**.

**Note:** Most of the custom styles in styles.css are created via `@apply some-tailwind-class;` as it is not possible to manually add CSS classes to elements that are created via jQuery.

## Pre-commit

Before adding any source code, it is recommended to have pre-commit installed on your local computer to check for potential issues when committing code.

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files # Check if everything is okay
```
