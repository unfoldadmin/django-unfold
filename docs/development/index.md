---
title: Development
order: 12
---

# Development

## Starting the testing server

The Unfold repository contains a testing server that you can use to test any changes you make to the code. To start the server, navigate to `tests/server` and run `uv run -- python manage.py migrate` then `uv run -- python manage.py runserver`. This will start the server at `http://localhost:8000`.

Before running the server, you don't need to install anything, as `uv` will automatically take care of the dependencies.

Once the server is running, you need to create a superuser account to access the admin interface. To create a superuser, run `uv run -- python manage.py createsuperuser`.

## Running tests locally

To run the tests, navigate to the root of the repository and run the command below. The tests will run in the `tests` directory. Again, it is not necessary to install anything, as `uv` will automatically take care of the dependencies.

```sh
uv run -- pytest .
```

## Compiling Tailwind

Unfold uses [Tailwind CSS](https://tailwindcss.com/) for styling and utility-first CSS classes. To work on or change styles, you'll need to compile Tailwind whenever you make updates to `src/unfold/styles.css` or related class usage.

### Installing Tailwind CLI

To compile Tailwind CSS, you must have the standalone [tailwindcss CLI](https://tailwindcss.com/docs/installation) installed.

**On macOS (using Homebrew):**

```sh
brew install tailwindcss
```

**On other platforms:**

You can download a prebuilt binary from the [Tailwind CSS release page](https://github.com/tailwindlabs/tailwindcss/releases) or follow instructions for your OS.


### Compiling CSS

After installing `tailwindcss`, compile your CSS with the following command (run from your project root):

```sh
tailwindcss -i src/unfold/styles.css -o src/unfold/static/unfold/css/styles.css --minify --watch
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
