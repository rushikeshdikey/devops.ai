import yaml
import re
from apps.api.schemas.validation import ValidationReport, ValidationIssue


def validate_k8s_yaml(content: str) -> ValidationReport:
    """Validate Kubernetes YAML configuration."""
    issues = []

    try:
        docs = list(yaml.safe_load_all(content))
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

    for idx, doc in enumerate(docs):
        if not doc:
            continue

        doc_path = f"document[{idx}]"

        # Check for apiVersion
        if "apiVersion" not in doc:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_API_VERSION",
                    message="Missing 'apiVersion' field",
                    path=doc_path,
                )
            )

        # Check for kind
        if "kind" not in doc:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_KIND",
                    message="Missing 'kind' field",
                    path=doc_path,
                )
            )

        # Check for metadata.name
        if "metadata" not in doc or "name" not in doc.get("metadata", {}):
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_METADATA_NAME",
                    message="Missing 'metadata.name' field",
                    path=doc_path,
                )
            )

        # Check containers if it's a Deployment/Pod/StatefulSet
        kind = doc.get("kind", "")
        if kind in ["Deployment", "Pod", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            spec = doc.get("spec", {})

            # Get containers based on kind
            if kind == "Pod":
                containers = spec.get("containers", [])
            elif kind == "CronJob":
                containers = spec.get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
            else:
                containers = spec.get("template", {}).get("spec", {}).get("containers", [])

            for cidx, container in enumerate(containers):
                container_path = f"{doc_path}.spec.containers[{cidx}]"

                # Check image
                image = container.get("image", "")
                if ":latest" in image or not ":" in image:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="LATEST_TAG_DISALLOWED",
                            message=f"Container image should not use ':latest' tag: {image}",
                            path=f"{container_path}.image",
                        )
                    )

                # Check resource requests/limits
                resources = container.get("resources", {})
                if not resources.get("requests"):
                    issues.append(
                        ValidationIssue(
                            level="WARN",
                            code="MISSING_RESOURCE_REQUESTS",
                            message=f"Container '{container.get('name', 'unknown')}' missing resource requests",
                            path=f"{container_path}.resources",
                        )
                    )

                if not resources.get("limits"):
                    issues.append(
                        ValidationIssue(
                            level="WARN",
                            code="MISSING_RESOURCE_LIMITS",
                            message=f"Container '{container.get('name', 'unknown')}' missing resource limits",
                            path=f"{container_path}.resources",
                        )
                    )

            # Check replicas for Deployment
            if kind == "Deployment":
                replicas = spec.get("replicas", 1)
                if replicas < 2:
                    issues.append(
                        ValidationIssue(
                            level="WARN",
                            code="LOW_REPLICA_COUNT",
                            message=f"Deployment has {replicas} replica(s). Consider using >= 2 for high availability",
                            path=f"{doc_path}.spec.replicas",
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
