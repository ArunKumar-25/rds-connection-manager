# Contributing

## Getting Started

1. Fork and clone
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Install the package in editable mode for development: `pip install -e .`

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

## Using issue and pull request templates

This repository includes GitHub templates for bug reports, feature requests, and pull requests.
- Use the Bug report template for bugs and unexpected behavior.
- Use the Feature request template for new ideas or improvements.
- Use the Pull request template when submitting code changes.
