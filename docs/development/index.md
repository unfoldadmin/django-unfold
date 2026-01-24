---
title: Development
order: 12
---

# Development

## Starting the testing server

The Unfold repository contains a testing server that you can use to test any changes you make to the code. To start the server, navigate to `tests/server` and run `uv run -- python manage.py runserver`. This will start the server at `http://localhost:8000`.

Before running the server, you don't need to install anything, as `uv` will automatically take care of the dependencies.

Once the server is running, you need to create a superuser account to access the admin interface. To create a superuser, run `uv run -- python manage.py createsuperuser`.

## Running tests locally

To run the tests, navigate to the root of the repository and run the command below. The tests will run in the `tests` directory. Again, it is not necessary to install anything, as `uv` will automatically take care of the dependencies.

```sh
uv run -- pytest .
```

## Developing with a changed Poetry path

If you want to develop a new feature or fix an issue directly in your project that uses Poetry for dependency management, you can link the `django-unfold` dependency in your `pyproject.toml` to the local repository. The prerequisites are to have `django-unfold` installed and to be using Poetry for dependency management at the same time.

### Poetry configuration

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
