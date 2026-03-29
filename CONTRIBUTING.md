# Contributing to Django Fundraising CRM

Thank you for your interest in contributing to the Django Fundraising CRM! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility and apologize when mistakes happen

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-fundraising-crm.git
   cd django-fundraising-crm
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/intrepid-g/django-fundraising-crm.git
   ```

## Development Setup

### Using Docker (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check if the issue already exists
2. Use the latest version to verify the bug still exists

When reporting bugs, include:
- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, Django version)

### Suggesting Features

- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this feature would be useful
- Consider potential implementation approaches

### Pull Requests

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following our coding standards

4. **Test your changes**:
   ```bash
   pytest
   ```

5. **Commit with a clear message** (see [Commit Messages](#commit-messages))

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub

## Coding Standards

### Python Style

We follow PEP 8 with these specifics:
- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single quotes for strings, double quotes for docstrings
- **Imports**: Grouped as stdlib, third-party, local; sorted alphabetically

### Django Conventions

- **Models**: Use `verbose_name` and `verbose_name_plural`
- **Views**: Prefer class-based views for complex logic
- **Templates**: Use template inheritance, keep logic minimal
- **URLs**: Use meaningful names for URL patterns

### API Conventions

- Use Django Ninja for API endpoints
- Include trailing slashes in URL patterns
- Return consistent response structures
- Document all endpoints

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
pytest donors/tests/

# Run specific test class
pytest donors/tests/test_models.py::DonorModelTests

# Run with verbose output
pytest -v
```

### Writing Tests

- All new features must include tests
- Tests should be in `tests/` directory within each app
- Use descriptive test method names
- Follow the Arrange-Act-Assert pattern

Example:
```python
def test_donor_creation_with_valid_data(self):
    """Test that a donor can be created with valid data."""
    # Arrange
    data = {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'}
    
    # Act
    donor = Donor.objects.create(**data)
    
    # Assert
    assert donor.first_name == 'Jane'
    assert donor.email == 'jane@example.com'
```

## Documentation

- Update README.md if you change functionality
- Update API.md for API changes
- Add docstrings to all public methods and classes
- Use Google-style docstrings:

```python
def process_donation(donor_id, amount, campaign_id=None):
    """Process a new donation.
    
    Args:
        donor_id: The ID of the donor making the donation
        amount: The donation amount as a Decimal
        campaign_id: Optional campaign to associate with the donation
        
    Returns:
        Donation: The created donation object
        
    Raises:
        ValueError: If amount is negative or zero
        Donor.DoesNotExist: If donor_id is invalid
    """
```

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, semicolons, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, etc.
- **ci**: CI/CD changes

### Examples

```
feat(donors): Add donor segmentation by donation amount

fix(api): Resolve trailing slash inconsistency in events endpoints

docs: Update API documentation for campaigns

test(donations): Add tests for recurring donation cancellation
```

## Pull Request Process

1. **Ensure tests pass**:
   ```bash
   pytest
   ```

2. **Update documentation** if needed

3. **Fill out the PR template**:
   - What does this PR do?
   - What issue does it fix? (use `Fixes #123`)
   - What tests were added?

4. **Request review** from maintainers

5. **Address review feedback** promptly

6. **Merge** once approved and CI passes

## Questions?

- Open an issue for questions
- Check existing documentation first
- Be specific about what you're trying to accomplish

Thank you for contributing! 🎉
