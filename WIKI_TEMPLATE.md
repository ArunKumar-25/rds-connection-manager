# RDS Connection Manager Wiki

This file is a sample outline for GitHub Wiki pages. Copy sections into the repository Wiki or use it as a starting point.

## Overview

- What the project does
- Key features
- Supported environments
- Typical use cases

## Installation

### Prerequisites

- Python 3.8+
- AWS CLI or boto3
- PostgreSQL client (`psql`)

### Setup

```bash
git clone https://github.com/ArunKumar-25/rds-connection-manager.git
cd rds-connection-manager
pip install -r requirements.txt
pip install -e .
```

## Configuration

### Database catalog

Explain `db_catalog.json` structure and example fields.

### Environment variables

- `RDS_CATALOG`
- `RDS_LOG`
- AWS credentials and region settings

## Usage

### List databases

```bash
python connect_rds_manager.py --list
```

### Connect to a database

```bash
python connect_rds_manager.py prod-main
```

### Preview connection

```bash
python connect_rds_manager.py prod-main --preview
```

## Troubleshooting

- psql not found
- AWS credentials missing
- Token generation failures

## Development

- How to run tests
- Formatting and linting
- How to contribute

## Release notes

- Add version changes and improvements here
