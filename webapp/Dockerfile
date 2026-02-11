# Advanced Memory webapp - build and serve
# Multi-stage: Node build, nginx serve

# --- build ---
FROM node:20-alpine AS build

WORKDIR /app

# Install deps
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Override API base URL at build time (default: bridge on host)
ARG VITE_API_URL=http://localhost:8001/api/v1
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# --- serve ---
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
