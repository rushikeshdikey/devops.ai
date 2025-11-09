from .k8s_yaml import validate_k8s_yaml
from .terraform import validate_terraform
from .generic_yaml import validate_generic_yaml
from apps.api.schemas.validation import ValidationReport


def get_validator(config_type: str):
    """Get the appropriate validator for a config type."""
    validators = {
        "K8S_YAML": validate_k8s_yaml,
        "TERRAFORM": validate_terraform,
        "GENERIC_YAML": validate_generic_yaml,
    }
    return validators.get(config_type, validate_generic_yaml)


def validate_content(content: str, config_type: str) -> ValidationReport:
    """Validate content based on its type."""
    validator = get_validator(config_type)
    return validator(content)
