"""
Compatibility layer for pydantic v1 and v2.

This module provides a unified interface for pydantic features that differ
between v1 and v2, allowing the codebase to work with both versions.
"""

import sys
from typing import Any, Dict, Type, Union

import pydantic

# Detect pydantic version
PYDANTIC_V2 = hasattr(pydantic, '__version__') and pydantic.__version__.startswith('2.')

if PYDANTIC_V2:
    from pydantic import ConfigDict, TypeAdapter, model_validator, model_serializer
    from pydantic.fields import FieldInfo
    
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration for v2."""
        return getattr(cls, 'model_config', {})
    
    def set_model_config(cls, config: Dict[str, Any]) -> None:
        """Set model configuration for v2."""
        cls.model_config = config
    
    def create_model_validator(mode: str = "before"):
        """Create model validator decorator for v2."""
        return model_validator(mode=mode)
    
    def create_model_serializer():
        """Create model serializer decorator for v2."""
        return model_serializer()
    
    def get_type_adapter(type_: Type) -> TypeAdapter:
        """Get TypeAdapter for v2."""
        return TypeAdapter(type_)
    
    def model_dump(instance: pydantic.BaseModel, **kwargs) -> Dict[str, Any]:
        """Model dump method for v2."""
        return instance.model_dump(**kwargs)
    
    def model_validate(cls: Type[pydantic.BaseModel], data: Any) -> pydantic.BaseModel:
        """Model validate method for v2."""
        return cls.model_validate(data)
    
    def json_schema(cls: Type[pydantic.BaseModel]) -> Dict[str, Any]:
        """Get JSON schema for v2."""
        return cls.model_json_schema()

else:
    # Pydantic v1 compatibility
    from pydantic import root_validator
    from pydantic.fields import FieldInfo
    
    class TypeAdapter:
        """Compatibility TypeAdapter for pydantic v1."""
        def __init__(self, type_: Type):
            self.type_ = type_
        
        def validate_python(self, data: Any) -> Any:
            """Validate python data using pydantic v1."""
            if hasattr(self.type_, '__origin__'):
                # Handle generic types
                return data
            elif hasattr(self.type_, 'parse_obj'):
                # Pydantic model
                return self.type_.parse_obj(data)
            elif hasattr(self.type_, '__call__'):
                # Built-in types or callable types
                try:
                    return self.type_(data)
                except (ValueError, TypeError):
                    return data
            else:
                return data
        
        def dump_python(self, data: Any, mode: str = "json") -> Any:
            """Dump python data using pydantic v1."""
            if hasattr(data, 'dict'):
                return data.dict()
            elif hasattr(data, '__dict__'):
                return data.__dict__
            else:
                return data
        
        def json_schema(self) -> Dict[str, Any]:
            """Get JSON schema using pydantic v1."""
            if hasattr(self.type_, 'schema'):
                return self.type_.schema()
            else:
                # Fallback for basic types
                type_name = getattr(self.type_, '__name__', str(self.type_))
                if type_name == 'str':
                    return {"type": "string"}
                elif type_name == 'int':
                    return {"type": "integer"}
                elif type_name == 'float':
                    return {"type": "number"}
                elif type_name == 'bool':
                    return {"type": "boolean"}
                elif type_name == 'list':
                    return {"type": "array"}
                elif type_name == 'dict':
                    return {"type": "object"}
                else:
                    return {"type": "string"}
    
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration for v1."""
        config_class = getattr(cls, 'Config', None)
        if config_class is None:
            return {}
        
        config_dict = {}
        for attr in dir(config_class):
            if not attr.startswith('_'):
                config_dict[attr] = getattr(config_class, attr)
        return config_dict
    
    def set_model_config(cls, config: Dict[str, Any]) -> None:
        """Set model configuration for v1."""
        # In v1, we don't set config during __init__ but rather on the class
        # We'll store the config to be applied later if needed
        if not hasattr(cls, '_pending_config'):
            cls._pending_config = config
    
    def create_model_validator(mode: str = "before"):
        """Create model validator decorator for v1."""
        def decorator(func):
            # In v1, we use @root_validator with pre=True for "before" mode
            pre = mode == "before"
            return root_validator(pre=pre, allow_reuse=True)(func)
        return decorator
    
    def create_model_serializer():
        """Create model serializer decorator for v1."""
        def decorator(func):
            # In v1, serialization is handled differently
            # We'll monkey-patch the method to be called by __str__ or similar
            return func
        return decorator
    
    def get_type_adapter(type_: Type) -> TypeAdapter:
        """Get TypeAdapter for v1."""
        return TypeAdapter(type_)
    
    def model_dump(instance: pydantic.BaseModel, **kwargs) -> Dict[str, Any]:
        """Model dump method for v1."""
        return instance.dict(**kwargs)
    
    def model_validate(cls: Type[pydantic.BaseModel], data: Any) -> pydantic.BaseModel:
        """Model validate method for v1."""
        return cls.parse_obj(data)
    
    def json_schema(cls: Type[pydantic.BaseModel]) -> Dict[str, Any]:
        """Get JSON schema for v1."""
        return cls.schema()

__all__ = [
    'PYDANTIC_V2',
    'TypeAdapter',
    'get_model_config',
    'set_model_config', 
    'create_model_validator',
    'create_model_serializer',
    'get_type_adapter',
    'model_dump',
    'model_validate',
    'json_schema',
] 