# Contributing

## Getting Started

1. Fork and clone
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`

## Testing

```bash
pytest test_connect_rds_manager.py -v
```

## Code Quality

Format with black:
```bash
black connect_rds_manager.py
```

Type check with mypy:
```bash
mypy connect_rds_manager.py --ignore-missing-imports
```

## Submitting Changes

- Make sure tests pass
- Format your code with black
- Submit a pull request with a clear description

## Bug Reports

Open an issue with:
- What you were trying to do
- What happened
- Error message or logs
- Python version
