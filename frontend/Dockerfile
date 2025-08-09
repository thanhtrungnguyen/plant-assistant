FROM node:22-bookworm

# Set the working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files and install dependencies
COPY package*.json pnpm-lock.yaml ./

# Install dependencies as root
RUN pnpm install --frozen-lockfile

# Copy the rest of your application code
COPY . .

# Make start.sh executable while still root
RUN chmod +x start.sh

# Switch to the non-root user
USER node

EXPOSE 3000

# Start the application
CMD ["./start.sh"]