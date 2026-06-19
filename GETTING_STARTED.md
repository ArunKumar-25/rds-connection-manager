# Getting Started

## Installation

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Setup

1. Copy the example catalog:
   ```bash
   cp db_catalog.example.json db_catalog.json
   ```

2. Edit `db_catalog.json` with your RDS database endpoints

3. Verify AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```

## Basic Usage

List all databases:
```bash
python connect_rds_manager.py --list
```

Connect to a database:
```bash
python connect_rds_manager.py prod-main
```

Preview connection:
```bash
python connect_rds_manager.py prod-main --preview
```

Connect as a specific user:
```bash
python connect_rds_manager.py prod-main --user admin
```

## Next Steps

- Read the README.md for detailed documentation
- Check the examples in CONTRIBUTING.md
- Review db_catalog.example.json for configuration details

## Troubleshooting

If psql is not found:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql
```

If AWS credentials fail:
```bash
aws configure
# Enter your access key, secret key, and region
```
