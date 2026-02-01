# Contributing to GhanaHomes

Thank you for your interest in contributing to GhanaHomes! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. **Check existing issues** - Avoid duplicates
2. **Provide details:**
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/error logs if applicable
   - Your environment (Python version, Django version, OS)

### Suggesting Features

1. **Check existing issues** - Avoid duplicates
2. **Describe the feature:**
   - What problem does it solve?
   - How should it work?
   - Example use cases
   - Alternative solutions considered

### Pull Requests

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/ghanahomes.git
cd ghanahomes

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows or source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Code Guidelines

1. **Python/Django Style:**
   - Follow PEP 8
   - Use meaningful variable names
   - Add docstrings to functions/classes
   - Keep functions small and focused

2. **Django Conventions:**
   - Use Django ORM (don't write raw SQL)
   - Create models with proper field types
   - Use Django forms for validation
   - Implement proper error handling

3. **Commit Messages:**
   - Use clear, descriptive messages
   - Start with verb: "Add", "Fix", "Update", "Remove"
   - Reference issue numbers: "Fix #123"
   - Example: `Add email verification for user signup (Fix #45)`

4. **Testing:**
   - Write tests for new features
   - Ensure existing tests pass
   - Test edge cases
   - Use meaningful test names

```bash
# Run tests
python manage.py test

# Run specific test
python manage.py test accounts.tests_auth

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

5. **Code Quality:**
   - Check code with flake8: `flake8 .`
   - Check imports: `isort --check-only .`
   - Format code: `black .`

#### Submitting a Pull Request

1. **Before submitting:**
   - Update documentation if needed
   - Ensure all tests pass
   - Check code style
   - Rebase with latest main branch

2. **Create Pull Request:**
   - Title: Clear, concise description
   - Description: Explain changes and why
   - Reference related issues
   - Include testing instructions if needed

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Related Issue
   Fixes #123
   
   ## Changes Made
   - Change 1
   - Change 2
   
   ## How to Test
   Steps to test the feature
   
   ## Checklist
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] Code follows style guidelines
   - [ ] All tests passing
   ```

## Development Workflow

### Project Structure
```
ghanahomes/
├── accounts/          # User authentication
├── properties/        # Property listings
├── payments/          # Payment integration
├── chat/              # Real-time messaging
├── subscriptions/     # Subscription management
└── ghanahomes/        # Project settings
```

### Common Development Tasks

**Create migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Create test file:**
```bash
# In accounts/tests_feature.py
from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('john', 'john@example.com', 'pass123')
    
    def test_user_creation(self):
        user = User.objects.get(username='john')
        self.assertEqual(user.email, 'john@example.com')
```

**Add new feature:**
1. Create model in `models.py`
2. Create migration
3. Create view in `views.py`
4. Create form in `forms.py` (if needed)
5. Add URL in `urls.py`
6. Create template in `templates/`
7. Add tests in `tests.py`
8. Update admin in `admin.py`
9. Update documentation

## Documentation

### Update docs when:
- Adding new features
- Changing existing functionality
- Adding admin features
- Changing deployment instructions

### Documentation standards:
- Use clear, concise language
- Include examples where helpful
- Use proper markdown formatting
- Include screenshots for UI changes
- Update README.md if relevant

## Community & Discussion

- **Issues** - For bugs and feature requests
- **Discussions** - For questions and ideas
- **Email** - For sensitive topics
- **Meetings** - Scheduled discussions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Added to GitHub contributors page

## Getting Help

- **Documentation** - See [docs/](docs/)
- **Issues** - Check existing discussions
- **Discussions** - Ask questions
- **Email** - Contact maintainer

## License

By contributing, you agree your code will be licensed under the MIT License.

---

Thank you for contributing to GhanaHomes! 🎉
