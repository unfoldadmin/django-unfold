FROM node:latest

ENV TAILWIND=/app

WORKDIR $TAILWIND

COPY package.json package-lock.json /$TAILWIND

RUN npm install

ENTRYPOINT ["npm","run", "watch"]
