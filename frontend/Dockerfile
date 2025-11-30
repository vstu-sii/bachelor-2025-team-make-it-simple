FROM node:25.2.1-trixie-slim

WORKDIR /app

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm install

RUN npm run build

# STAGE 1

FROM nginx:alpine3.22
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]