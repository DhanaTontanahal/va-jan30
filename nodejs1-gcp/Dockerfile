# Use the official Node.js image as a base
FROM node:18-alpine as build

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the application code
COPY . .

# Install the Cloud SQL Auth Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy && chmod +x /cloud_sql_proxy

# Expose the port Cloud Run will use (documentation purposes)
EXPOSE 8080

# Set environment variables for Cloud SQL Proxy
ENV INSTANCE_CONNECTION_NAME="voltaic-battery-447511-p5:us-central1:va-db"
ENV DB_USER="root"
ENV DB_PASS="yourpassword"
ENV DB_NAME="menu-logger"

# Ensure Node.js app listens on Cloud Run's PORT environment variable
ENV PORT=8080

# Start the Cloud SQL Auth Proxy and the Node.js application
CMD ["sh", "-c", "/cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:3306 & node index.js"]
