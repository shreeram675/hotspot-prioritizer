# Build Stage
FROM node:18-slim as build

WORKDIR /app

COPY cityreport/package.json cityreport/package-lock.json* ./
RUN npm install
RUN npm rebuild esbuild

COPY cityreport/ .
RUN npm run build

# Serve Stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy custom nginx config if needed (we will use the root nginx for reverse proxy, 
# but this nginx serves static files)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
