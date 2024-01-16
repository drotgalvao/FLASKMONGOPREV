# Dockerfile for React (Node.js 18.16.0) app

# Use Alpine Linux as base image
FROM node:18.16.0-alpine

WORKDIR /app

COPY package.json .
RUN npm i

COPY . .

## EXPOSE [Port you mentioned in the vite.config file]

EXPOSE 5173

CMD ["npm", "run", "dev"]