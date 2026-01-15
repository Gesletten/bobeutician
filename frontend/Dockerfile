# Using official Node.js :18 image for base
FROM node:18-alpine

# Set up the working directory inside container

WORKDIR /app

# First copy only dependency files for caching leverage
# Use files relative to the build context (./frontend) instead of
# referencing a non-existent `frontend/` subpath inside the context.
COPY package*.json ./

# Installing any dependencies
RUN npm install

# Finish copying rest of frontend source code
# Copy everything from the build context (which is the frontend folder)
COPY . .

# Expose port
EXPOSE 3000

#Start the development server
CMD ["npm", "run", "dev"]
