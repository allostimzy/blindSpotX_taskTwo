# Azure Resource Drift Management

A comprehensive solution for detecting and managing configuration drift in Azure resources.

## Features

- Real-time drift detection for Azure resources
- Severity-based drift classification (CRITICAL, HIGH, MEDIUM, LOW)
- Structured logging and metrics collection
- Prometheus and Grafana integration for visualization
- Automated testing and CI/CD pipeline
- Docker containerization
- Noise-tolerant drift detection algorithm

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Azure subscription and credentials
- PostgreSQL database

## Installation

1. Clone the repository:


2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirement.txt
```

4. Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running with Docker

1. Build and start the containers:

```bash
docker-compose up --build
```

2. Access the services:

- Web Application: http://localhost:5000
- Grafana Dashboard: http://localhost:3000
- Prometheus: http://localhost:9090

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses:

- Black for code formatting
- Flake8 for linting
- MyPy for type checking

Run the checks:

```bash
black .
flake8
mypy .
```

## Architecture

### Components

1. **Drift Detection Engine**

   - Implements noise-tolerant drift detection algorithm
   - Severity classification system
   - Data normalization for handling noisy data

2. **Monitoring Stack**

   - Prometheus for metrics collection
   - Grafana for visualization
   - Structured logging with JSON format

3. **API Layer**
   - RESTful endpoints for drift management
   - Authentication and authorization
   - Rate limiting and request validation

### Data Flow

1. Azure resources are monitored continuously
2. Configuration snapshots are compared using the drift detection algorithm
3. Drift events are classified by severity
4. Metrics and logs are collected and stored
5. Visualizations are updated in real-time

## CI/CD Pipeline

The project includes a GitHub Actions workflow that:

- Runs automated tests
- Performs code quality checks
- Builds and pushes Docker images
- Deploys to production (if tests pass)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For support, please open an issue in the GitHub repository.
