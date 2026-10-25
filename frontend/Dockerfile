FROM node:26-alpine AS build

WORKDIR /app

# Install dependencies first for better Docker layer caching.
COPY package.json package-lock.json ./

RUN npm ci

# Vite embeds VITE_* variables during the build.
ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy the frontend source.
COPY . .

# Create the production build.
RUN npm run build


FROM nginx:alpine

# Copy the Vite production build into Nginx's web root.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
