import re
from apps.api.schemas.validation import ValidationReport, ValidationIssue


def validate_terraform(content: str) -> ValidationReport:
    """Validate Terraform configuration using heuristics."""
    issues = []

    # Check for provider block
    if not re.search(r'provider\s+"', content):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="MISSING_PROVIDER",
                message="No provider block found",
                path=None,
            )
        )

    # Check for resource blocks
    resource_matches = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', content)
    if not resource_matches:
        issues.append(
            ValidationIssue(
                level="WARN",
                code="NO_RESOURCES",
                message="No resource blocks found",
                path=None,
            )
        )

    # Check for required tags (environment, owner)
    for resource_type, resource_name in resource_matches:
        # Find the resource block
        pattern = rf'resource\s+"{resource_type}"\s+"{resource_name}"\s*{{([^}}]*(?:{{[^}}]*}}[^}}]*)*)}}'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            resource_content = match.group(1)

            # Check for tags block
            if "tags" in resource_content:
                tags_match = re.search(r'tags\s*=\s*{([^}]*)}', resource_content, re.DOTALL)
                if tags_match:
                    tags_content = tags_match.group(1)

                    # Check for required tag keys
                    if "environment" not in tags_content.lower():
                        issues.append(
                            ValidationIssue(
                                level="WARN",
                                code="MISSING_ENVIRONMENT_TAG",
                                message=f"Resource '{resource_type}.{resource_name}' missing 'environment' tag",
                                path=f"resource.{resource_type}.{resource_name}",
                            )
                        )

                    if "owner" not in tags_content.lower():
                        issues.append(
                            ValidationIssue(
                                level="WARN",
                                code="MISSING_OWNER_TAG",
                                message=f"Resource '{resource_type}.{resource_name}' missing 'owner' tag",
                                path=f"resource.{resource_type}.{resource_name}",
                            )
                        )
            else:
                issues.append(
                    ValidationIssue(
                        level="WARN",
                        code="MISSING_TAGS",
                        message=f"Resource '{resource_type}.{resource_name}' has no tags block",
                        path=f"resource.{resource_type}.{resource_name}",
                    )
                )

    # Check for variable declarations and usage
    declared_vars = set(re.findall(r'variable\s+"([^"]+)"', content))
    used_vars = set(re.findall(r'var\.([a-zA-Z_][a-zA-Z0-9_]*)', content))

    unused_vars = declared_vars - used_vars
    for var in unused_vars:
        issues.append(
            ValidationIssue(
                level="INFO",
                code="UNUSED_VARIABLE",
                message=f"Variable '{var}' declared but not used",
                path=f"variable.{var}",
            )
        )

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
