# Docker Deployment Guide

This guide explains how to deploy the PDF Converter API using Docker.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pdfconvertorapi
   ```

2. Build and start the containers:
   ```
   docker-compose up -d
   ```

3. The API will be available at http://localhost:8000

## Configuration

The application uses environment variables for configuration. The default production settings are in the `.env.production` file.

You can modify the following settings:

- `ENVIRONMENT`: Set to "production" for production deployment
- `MAX_FILE_SIZE`: Maximum allowed file size in bytes (default: 20MB)
- `RATE_LIMIT`: API rate limiting (default: 500/day)
- `CORS_ORIGINS`: Comma-separated list of allowed origins for CORS
- `TEMP_DIR`: Directory for temporary files (default: /app/tmp)
- `FILE_EXPIRY_HOURS`: Hours before converted files are deleted (default: 12)

## Volume Mapping

The docker-compose.yml maps the local `tmp` directory to `/app/tmp` in the container. This ensures that temporary files persist between container restarts.

## Scaling

To scale the service, you can use:

```
docker-compose up -d --scale api=3
```

Note that you will need a load balancer in front of the API instances for proper scaling.

## Monitoring

You can check the container logs with:

```
docker-compose logs -f
```

## Updating

To update to a new version:

1. Pull the latest code:
   ```
   git pull
   ```

2. Rebuild and restart the containers:
   ```
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

## Troubleshooting

If you encounter issues, check:

1. Container logs: `docker-compose logs -f`
2. Ensure the tmp directory is writable
3. Verify that the environment variables are set correctly
