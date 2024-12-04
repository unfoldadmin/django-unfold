---
title: Development
order: 12
description: Development guide and best practices for Unfold.
---

# Development

## Pre-commit

Before adding any source code, it is recommended to have pre-commit installed on your local computer to check for all potential issues when committing the code.

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit run --all-files # Check if everything is okay
```

## Poetry configuration

To add a new feature or fix the easiest approach is to use django-unfold in combination with Poetry. The process looks like:

- Install django-unfold via `poetry add django-unfold`
- After that it is needed to git clone the repository somewhere on local computer.
- Edit _pyproject.toml_ and update django-unfold line `django-unfold = { path = "../django-unfold", develop = true}`
- Lock and update via `poetry lock && poetry update`

## Compiling Tailwind

At the moment project contains package.json with all dependencies required to compile new CSS file. Tailwind configuration file is set to check all html, js and py files for Tailwind's classes occurrences.

```bash
npm install
npx tailwindcss -i src/unfold/styles.css -o src/unfold/static/unfold/css/styles.css --watch --minify

npm run tailwind:watch # run after each change in code
npm run tailwind:build # run once
```

Some components like datepickers, calendars or selectors in admin was not possible to style by overriding html templates so their default styles are overridden in **styles.css**.

**Note:** most of the custom styles located in style.css are created via `@apply some-tailwind-class;` as is not possible to manually add CSS class to element which are for example created via jQuery.

## Design system

| Component                         | Classes                                                |
| --------------------------------- | ------------------------------------------------------ |
| Regular text                      | text-gray-600 dark:text-gray-300                       |
| Hover regular text                | text-gray-700 dark:text-gray-200                       |
| Headings                          | font-semibold text-gray-900 dark:text-gray-100         |
| Icon                              | text-gray-400 dark:text-gray-500                       |
| Hover icon                        | hover:text-gray-500 dark:hover:text-gray-400           |

## Using VS Code with containers

Unfold already contains prepared support for VS Code development. After cloning the project locally, open the main folder in VS Code (in terminal `code .`). Immediately, you would see a message from VS Code **Folder contains a Dev Container configuration file. Reopen folder to develop in a container** which will inform you that the support for containers is prepared. Confirm the message by clicking on **Reopen in Container**. If the message is not there, you can still manually open the project in a container by running the command **Dev Containers: Reopen in Container**.

### Development server

Now the VS Code will build an image and install Python dependencies. After successful installation is completed, VS Code will spin a container and from now it is possible to directly develop in the container. Unfold contains an example development application with the basic Unfold configuration available under `tests/server`. Run `python manage.py runserver` within a `tests/server` folder to start a development Django server. Note that you have to run the command from VS Code terminal which is already connected to the running container.

**Note:** this is not a production ready server. Use it just for running tests or developing features & fixes.

### Compiling Tailwind in devcontainer

The container has already a node preinstalled so it is possible to compile a new CSS. Open the terminal and run `npm install` which will install all dependencies and will create `node_modules` folder. Now, you can run npm commands for Tailwind as described in the previous chapter.
