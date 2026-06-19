# RDS Connection Manager

[![CI](https://github.com/ArunKumar-25/rds-connection-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/ArunKumar-25/rds-connection-manager/actions)
[![Python](https://img.shields.io/pypi/pyversions/rds-connection-manager?color=blue&label=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Python utility for connecting to AWS RDS databases using IAM authentication. It handles token generation, database catalog management, and connection logging.

## Features

- IAM-based authentication (no hardcoded passwords)
- Database catalog management
- Connection logging and audit trail
- Interactive and non-interactive modes
- Supports both boto3 and AWS CLI

## Requirements

- Python 3.8 or higher
- boto3 (optional but recommended)
- AWS CLI (as fallback)
- PostgreSQL client (psql)

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/ArunKumar-25/rds-connection-manager.git
cd rds-connection-manager
pip install -r requirements.txt
```

This repository includes an example catalog file at `db_catalog.example.json`.

To use as a command-line tool:

```bash
pip install -e .
```

## Contributing

Please read `CONTRIBUTING.md` before opening issues or pull requests. Use the GitHub issue and PR templates in `.github/` to provide complete information.

## Configuration

### Database Catalog

Create a `db_catalog.json` file with your database configurations:

```json
[
  {
    "alias": "prod-main",
    "dbname": "production_db",
    "db_endpoint": "prod-db.abcdef.ap-south-1.rds.amazonaws.com",
    "port": 5432,
    "region": "ap-south-1",
    "account_id": "123456789012",
    "env": "prod"
  },
  {
    "alias": "staging-analytics",
    "dbname": "staging_analytics",
    "db_endpoint": "staging-db.ghijkl.ap-south-1.rds.amazonaws.com",
    "port": 5432,
    "region": "ap-south-1",
    "account_id": "123456789012",
    "env": "staging"
  }
]
```

Required fields:
- `alias` - Short name for the database
- `dbname` - Actual PostgreSQL database name
- `db_endpoint` - RDS endpoint hostname
- `port` - Database port (default 5432)
- `region` - AWS region
- `account_id` - AWS account ID
- `env` - Environment tag (prod, staging, dev)

### Environment Variables

```bash
# Override default catalog location
export RDS_CATALOG=/path/to/custom_catalog.json

# Set log file location
export RDS_LOG=/path/to/connection.log
```

## Usage

### List available databases

```bash
python connect_rds_manager.py --list
```

### Connect to a database

```bash
# Basic connection
python connect_rds_manager.py prod-main

# Connect as specific user
python connect_rds_manager.py prod-main --user admin

# Non-interactive mode
python connect_rds_manager.py prod-main --no-prompt

# Preview connection without connecting
python connect_rds_manager.py prod-main --preview
```

### Search for databases

```bash
# Partial name search
python connect_rds_manager.py analytics

# Get suggestions for typos
python connect_rds_manager.py prod-mai
```

### Enable verbose logging

```bash
python connect_rds_manager.py prod-main --verbose
```

## Usage Examples

```bash
# List all databases
python connect_rds_manager.py --list

# Connect to a database
python connect_rds_manager.py prod-main

# Preview before connecting
python connect_rds_manager.py prod-main --preview

# Connect as specific user
python connect_rds_manager.py prod-main --user admin

# Non-interactive mode
python connect_rds_manager.py prod-main --no-prompt
```

## How It Works

1. Loads your database catalog from JSON
2. Resolves username from environment or AWS identity
3. Generates temporary IAM token (15 min expiry)
4. Logs connection attempt
5. Opens psql session with the token as password

No passwords are stored or hardcoded - authentication happens entirely through AWS IAM.

## Troubleshooting

**psql not found:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql
```

**AWS credentials not configured:**
```bash
aws configure
```

**Token generation fails:**
Check that your IAM user has `rds-db:connect` permission.

## Troubleshooting

### psql: command not found

Install the PostgreSQL client:

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### AWS credentials not found

Configure AWS credentials:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=ap-south-1
```

### Token generation failed

Verify IAM permissions:

```bash
aws rds describe-db-instances --region ap-south-1
```

Ensure your IAM user has permissions for:
- `rds-db:connect`
- `sts:GetCallerIdentity`

## License

MIT
