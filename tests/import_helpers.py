"""Helper functions for importing modules with hyphenated directory names"""
import sys
import importlib.util
from pathlib import Path


def import_service_module(service_name: str, module_name: str = "main"):
    """
    Import a service module, handling hyphenated directory names.
    
    Args:
        service_name: Service name (e.g., 'auth-service' or 'llm-service')
        module_name: Module name (default: 'main')
        
    Returns:
        Imported module
    """
    project_root = Path(__file__).parent.parent
    service_path = project_root / "services" / service_name / f"{module_name}.py"
    
    if not service_path.exists():
        raise ImportError(f"Module not found: {service_path}")
    
    spec = importlib.util.spec_from_file_location(
        f"{service_name.replace('-', '_')}_{module_name}",
        service_path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    return module


def import_shared_module(module_name: str):
    """
    Import a shared module.
    
    Args:
        module_name: Module name (e.g., 'redis_client', 'db_client')
        
    Returns:
        Imported module
    """
    project_root = Path(__file__).parent.parent
    module_path = project_root / "shared" / "common" / f"{module_name}.py"
    
    if not module_path.exists():
        raise ImportError(f"Module not found: {module_path}")
    
    spec = importlib.util.spec_from_file_location(
        f"shared.common.{module_name}",
        module_path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    return module

