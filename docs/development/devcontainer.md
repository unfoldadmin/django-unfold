---
title: VS Code devcontainers
order: 1
description: Learn how to set up and use VS Code devcontainers for efficient Unfold theme development, including Tailwind compilation and development server configuration.
---

# Using VS Code with containers

Unfold already contains prepared support for VS Code development. After cloning the project locally, open the main folder in VS Code (in terminal using `code .`). You will immediately see a message from VS Code stating **Folder contains a Dev Container configuration file. Reopen folder to develop in a container**. This indicates that container support is ready. Click on **Reopen in Container** to proceed. If you don't see this message, you can still manually open the project in a container by running the command **Dev Containers: Reopen in Container**.

## Development server

VS Code will build an image and install Python dependencies. After the installation is complete, VS Code will start a container where you can develop directly. Unfold contains an example development application with basic Unfold configuration available in the `tests/server` directory. To start a development Django server, navigate to the `tests/server` folder and run `python manage.py runserver 0.0.0.0:8000`. Make sure to run this command from the VS Code terminal that is connected to the running container.

**Note:** This is not a production-ready server. Use it only for running tests or developing features & fixes.

## Compiling Tailwind in devcontainer

Before building the styles, you need to install node dependencies since the current Docker image only contains Python dependencies. To enable node in the container, update the `.devcontainer/devcontainer.json` file by adding the following:

```json
// .devcontainer/devcontainer.json

"features": {
  "ghcr.io/devcontainers/features/node:1": {
    "version": "latest"
  }
}
```

This modification is necessary because the `features` are not functioning correctly in Cursor. This approach ensures compatibility with both Cursor and VS Code. Please note that after this change, the container will only work in VS Code and will require more time to start. After making this change, you must rebuild the container by running `Dev Containers: Rebuild Container` in VS Code.

Open the terminal and run `npm install` to install all dependencies and create the `node_modules` folder. You can then use the following npm commands for Tailwind:

```bash
# Run during development to watch for changes
npm run tailwind:watch

# Run for a one-time build
npm run tailwind:build
```

## Running without VS Code

If you prefer to run the project without VS Code, you can use `docker compose up` from the `.devcontainer` folder. This will automatically start a container and run the migrations and development server.
