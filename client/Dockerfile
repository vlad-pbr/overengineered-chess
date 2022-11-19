FROM docker.io/library/node:18.12.0-alpine as build
EXPOSE 80
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --loglevel verbose --no-audit
COPY . .
RUN npm run build --prod

FROM docker.io/library/nginx:1.22.1
COPY build/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/chess /usr/share/nginx/html