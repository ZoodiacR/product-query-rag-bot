# Stage 1: Build the React application
FROM node:20-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
# This helps Docker re-use cached layers if dependencies haven't changed
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend application code
COPY . .

# Build the React application
# Vite's default build command outputs the static files to the 'dist' directory
RUN npm run build

# Stage 2: Serve the application with Nginx for production-ready serving
# Using a very lightweight Nginx image
FROM nginx:alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration for SPAs
# This config is crucial for client-side routing (e.g., React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the build stage into Nginx's serving directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80, which is Nginx's default HTTP port
EXPOSE 80

# Command to start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
