# DSPy Pydantic Compatibility Guide

DSPy now supports both Pydantic v1 and v2, with automatic detection and compatibility handling. This guide explains how to work with different Pydantic versions and resolve dependency conflicts.

## 🔄 Automatic Compatibility

DSPy automatically detects your Pydantic version and adapts accordingly:
- **Pydantic v1.x**: Uses compatibility layer for v2 features
- **Pydantic v2.x**: Uses native Pydantic v2 features

## 📦 Installation Options

### Option 1: Pydantic v2 (Recommended)
```bash
pip install dspy
# This installs with Pydantic v2 by default
```

### Option 2: Pydantic v1
```bash
pip install "pydantic>=1.10.0,<2.0.0" dspy
```

### Option 3: With Poetry
```bash
# For Pydantic v1
poetry add "pydantic>=1.10.0,<2.0.0" dspy

# For Pydantic v2
poetry add "pydantic>=2.0.0,<3.0.0" dspy
```

## ⚠️ Handling Dependency Conflicts

Some optional dependencies require specific Pydantic versions:

### Weaviate Integration
- **Pydantic v2**: Use `pip install dspy[weaviate]`
- **Pydantic v1**: Use `pip install dspy[weaviate-v1-compat]` (limited features)

### LangChain Integration
- **Pydantic v2**: Use `pip install dspy[langchain]`
- **Pydantic v1**: May have limited compatibility

### Anthropic Integration
- Works with both Pydantic v1 and v2: `pip install dspy[anthropic]`

## 🧪 Verification

Test your installation:

```python
import dspy
from dspy.utils.pydantic_compat import PYDANTIC_V2

# Check Pydantic version
print(f"Using Pydantic v{'2' if PYDANTIC_V2 else '1'}")

# Test basic functionality
image = dspy.Image.from_url("https://example.com/image.jpg")
print(f"Image created successfully: {image}")

# Test custom types
history = dspy.History(messages=[{"role": "user", "content": "Hello"}])
print(f"History created successfully: {history}")
```

## 🔧 Advanced Configuration

### Manual Pydantic Version Selection
If you need to force a specific version for testing:

```python
# This is for testing only - normally auto-detection works
import os
os.environ['DSPY_FORCE_PYDANTIC_V1'] = 'true'  # Force v1 compatibility mode
import dspy
```

### Custom Model Configuration
The compatibility layer handles model configuration automatically:

```python
from dspy.adapters.types import Image

# This works with both Pydantic v1 and v2
class CustomImage(Image):
    custom_field: str = "default"
    
    # No need to manually set model_config
    # DSPy handles this automatically
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors with LiteLLM Streaming**
   ```python
   # DSPy handles this automatically with fallbacks
   # No action needed from users
   ```

2. **Dependency Version Conflicts**
   ```bash
   # Remove conflicting package and reinstall
   pip uninstall weaviate-client
   pip install dspy[weaviate-v1-compat]  # For Pydantic v1
   ```

3. **Validation Errors**
   ```python
   # Use keyword arguments instead of positional
   image = dspy.Image(url="https://example.com/image.jpg")  # ✅ Correct
   # image = dspy.Image("https://example.com/image.jpg")   # ❌ May fail
   ```

### Getting Help

If you encounter issues:
1. Check that you're using keyword arguments with DSPy types
2. Verify your Pydantic version: `python -c "import pydantic; print(pydantic.__version__)"`
3. Run the verification script above
4. Report issues with your environment details

## 📋 Migration Guide

### From DSPy with Pydantic v2 to v1
```bash
# 1. Install Pydantic v1
pip install "pydantic>=1.10.0,<2.0.0"

# 2. Update optional dependencies if needed
pip uninstall weaviate-client
pip install dspy[weaviate-v1-compat]

# 3. No code changes needed - DSPy handles compatibility
```

### From DSPy with Pydantic v1 to v2
```bash
# 1. Install Pydantic v2
pip install "pydantic>=2.0.0,<3.0.0"

# 2. Update to full-featured optional dependencies
pip install dspy[weaviate,langchain]

# 3. No code changes needed - DSPy handles compatibility
```

## ✅ Compatibility Matrix

| Feature | Pydantic v1 | Pydantic v2 |
|---------|-------------|-------------|
| Basic DSPy Types | ✅ | ✅ |
| Image/Audio/History | ✅ | ✅ |
| Tool Integration | ✅ | ✅ |
| JSON Schema | ✅ | ✅ |
| Model Validation | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Weaviate (full) | ⚠️ Limited | ✅ |
| LangChain | ⚠️ Limited | ✅ |
| Anthropic | ✅ | ✅ |

Legend: ✅ Full support, ⚠️ Limited support, ❌ Not supported

---

**Note**: This compatibility layer ensures DSPy works seamlessly regardless of your Pydantic version choice. The automatic detection and adaptation happen transparently, so you can focus on building with DSPy without worrying about version conflicts.