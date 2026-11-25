FROM node:24-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS dev
RUN apk add --no-cache git make \
    && git config --system --add safe.directory /repo
COPY . .
EXPOSE 5173
CMD ["make", "dev"]

FROM base AS build
ARG VITE_API_MOCKS=false
ENV VITE_API_MOCKS=$VITE_API_MOCKS
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
