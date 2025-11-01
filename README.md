# NetWorthy
A Net Worth Tool inspired by the Money Guy show and their Excel tool.

## Description
NetWorthy is a Flask-based web application that helps you track and analyze your net worth over time. It allows you to record assets, liabilities, and income, and provides analysis based on the Money Guy wealth accumulation metrics.

## Deployment

### Docker Deployment (Recommended)

#### Using Docker Compose (Easiest)

1. Clone the repository:
```bash
git clone https://github.com/JG3233/NetWorthy.git
cd NetWorthy
```

2. Start the application:
```bash
docker-compose up -d
```

3. Access the application at `http://localhost:5000`

4. To stop the application:
```bash
docker-compose down
```

#### Using Docker CLI

1. Build the Docker image:
```bash
docker build -t networthy .
```

2. Run the container:
```bash
docker run -d \
  --name networthy-app \
  -p 5000:5000 \
  -v $(pwd)/net_worth_history.json:/app/net_worth_history.json \
  networthy
```

3. Access the application at `http://localhost:5000`

4. To stop the container:
```bash
docker stop networthy-app
docker rm networthy-app
```

### Traditional Python Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

## Data Persistence

Your net worth data is stored in `net_worth_history.json`. When using Docker:
- The file is mounted as a volume to persist data between container restarts
- Make sure to back up this file regularly
- You can copy existing data by placing your `net_worth_history.json` file in the project directory before starting the container

## VM Deployment

To deploy on a VM:

1. Install Docker and Docker Compose on your VM
2. Clone this repository
3. Run `docker-compose up -d`
4. Configure your firewall to allow access to port 5000
5. (Optional) Set up a reverse proxy like nginx for HTTPS support

## Features

- Track assets (cash, investments, business interests, property)
- Track liabilities
- Track income
- Multi-year data tracking
- Analysis based on Money Guy wealth accumulation metrics (PAW/AAW/UAW)
- Clean, simple web interface
