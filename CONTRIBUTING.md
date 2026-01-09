# Contributing to ECFR Metrics

Thank you for your interest in contributing to ECFR Metrics! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable
- Environment details (OS, Python/Node versions)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature has already been requested
- Provide a clear description of the feature
- Explain the use case and benefits
- Consider implementation complexity

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/abou-diop/ecfr-metric.git
   cd ecfr-metric
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test your changes**
   - Backend: Test all API endpoints
   - Frontend: Test UI functionality and responsiveness
   - Verify end-to-end integration

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Add docstrings for public functions

Example:
```python
def parse_xml(content: bytes) -> Dict[str, Any]:
    """
    Parse ECFR XML content and extract metrics.
    
    Args:
        content: Raw XML file content
        
    Returns:
        Dictionary containing computed metrics
    """
    # Implementation
```

### TypeScript/React (Frontend)
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Keep components focused and reusable

Example:
```typescript
interface MetricsProps {
  data: MetricsData;
}

export default function MetricsDisplay({ data }: MetricsProps) {
  // Implementation
}
```

### Git Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Provide detailed description if needed

Good examples:
- `Add XML validation for file uploads`
- `Fix pie chart rendering issue`
- `Update documentation for Docker setup`

## Development Workflow

1. Set up your development environment (see DEVELOPMENT.md)
2. Create a feature branch
3. Make incremental commits
4. Test thoroughly
5. Update documentation
6. Submit a pull request

## Testing Requirements

### Backend Tests
- Test all new API endpoints
- Verify XML parsing with various inputs
- Check error handling

### Frontend Tests
- Test UI components
- Verify data visualization
- Check responsive design
- Test file upload functionality

## Documentation

When adding new features:
- Update README.md if necessary
- Update DEVELOPMENT.md for developer-facing changes
- Add code comments for complex logic
- Update API documentation

## Questions?

If you have questions about contributing:
- Open a GitHub issue with the "question" label
- Review existing documentation (README.md, DEVELOPMENT.md)
- Check closed issues for similar questions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to ECFR Metrics! 🎉
