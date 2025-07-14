# Contributing to Translation API

Thank you for your interest in contributing to Translation API! We welcome contributions from the community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/translation-api.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the service locally
uvicorn app:app --reload
```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep line length under 100 characters

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_translation.py::test_function_name
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the requirements.txt if you add dependencies
3. Ensure all tests pass
4. Update documentation as needed
5. Request review from maintainers

## Reporting Issues

- Use the issue templates provided
- Include steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version, etc.)

## Language Support

When adding new language support:
1. Add the language code mapping to `config.py`
2. Test the translation with sample texts
3. Update the README with the new language

## Performance Improvements

When optimizing performance:
1. Benchmark before and after changes
2. Document the performance gains
3. Ensure backward compatibility

## Questions?

Feel free to open an issue for any questions about contributing.