FROM docker.io/library/node:18.12.0-slim as build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build --prod

FROM docker.io/library/nginx:1.22.1
COPY --from=build /app/dist/chess /usr/share/nginx/html