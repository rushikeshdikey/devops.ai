FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json ./
COPY apps/web/package.json ./apps/web/

# Install dependencies
RUN npm install --workspace=apps/web

# Copy application code
COPY apps/web ./apps/web

WORKDIR /app/apps/web

# Expose port
EXPOSE 5173

# Run dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
