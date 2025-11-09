import yaml
from apps.api.schemas.validation import ValidationReport, ValidationIssue


MAX_SIZE_BYTES = 1024 * 1024  # 1MB


def validate_generic_yaml(content: str) -> ValidationReport:
    """Validate generic YAML configuration."""
    issues = []

    # Check size
    content_size = len(content.encode("utf-8"))
    if content_size > MAX_SIZE_BYTES:
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="FILE_TOO_LARGE",
                message=f"File size {content_size} bytes exceeds maximum {MAX_SIZE_BYTES} bytes",
                path=None,
            )
        )
        return ValidationReport(status="FAIL", issues=issues)

    # Parse YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="INVALID_YAML",
                message=f"Invalid YAML syntax: {str(e)}",
                path=None,
            )
        )
        return ValidationReport(status="FAIL", issues=issues)

    # Check if root is a mapping
    if not isinstance(data, dict):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="ROOT_NOT_MAPPING",
                message="YAML root must be a mapping (dictionary)",
                path=None,
            )
        )

    # Check for non-snake_case keys (warning only)
    def check_keys(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(key, str):
                    # Check if key is not snake_case
                    if not key.islower() or " " in key or "-" in key:
                        if not key.replace("_", "").replace("-", "").isalnum():
                            continue  # Skip special characters

                        if key != key.lower() or " " in key:
                            issues.append(
                                ValidationIssue(
                                    level="WARN",
                                    code="NON_SNAKE_CASE_KEY",
                                    message=f"Key '{key}' is not in snake_case format",
                                    path=f"{path}.{key}" if path else key,
                                )
                            )

                new_path = f"{path}.{key}" if path else key
                check_keys(value, new_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                check_keys(item, f"{path}[{idx}]")

    if isinstance(data, dict):
        check_keys(data)

    # Determine overall status
    has_errors = any(issue.level == "ERROR" for issue in issues)
    has_warnings = any(issue.level == "WARN" for issue in issues)

    if has_errors:
        status = "FAIL"
    elif has_warnings:
        status = "WARN"
    else:
        status = "PASS"

    return ValidationReport(status=status, issues=issues)
