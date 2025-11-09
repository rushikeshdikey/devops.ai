import re
from typing import List, Dict, Any


class PolicyEvaluationResult:
    """Result of policy evaluation."""

    def __init__(self, passed: bool, messages: List[str] = None):
        self.passed = passed
        self.messages = messages or []


class PolicyEngine:
    """A simple, safe policy evaluation engine."""

    @staticmethod
    def evaluate(rule: str, content: str) -> PolicyEvaluationResult:
        """
        Evaluate a policy rule against content.

        Supported expressions:
        - INCLUDES('text') - check if content contains text
        - MATCHES('pattern') - check if content matches regex pattern
        - NOT expr - negate expression
        - expr AND expr - logical AND
        - expr OR expr - logical OR

        Example: INCLUDES('owner:') AND NOT MATCHES(':\\s*latest\\b')
        """
        try:
            result = PolicyEngine._evaluate_expression(rule, content)
            return PolicyEvaluationResult(
                passed=result, messages=[] if result else ["Policy rule failed"]
            )
        except Exception as e:
            return PolicyEvaluationResult(passed=False, messages=[f"Error evaluating policy: {str(e)}"])

    @staticmethod
    def _evaluate_expression(expr: str, content: str) -> bool:
        """Recursively evaluate an expression."""
        expr = expr.strip()

        # Handle OR (lowest precedence)
        if " OR " in expr:
            parts = expr.split(" OR ")
            return any(PolicyEngine._evaluate_expression(part, content) for part in parts)

        # Handle AND
        if " AND " in expr:
            parts = expr.split(" AND ")
            return all(PolicyEngine._evaluate_expression(part, content) for part in parts)

        # Handle NOT
        if expr.startswith("NOT "):
            inner = expr[4:].strip()
            return not PolicyEngine._evaluate_expression(inner, content)

        # Handle INCLUDES
        includes_match = re.match(r"INCLUDES\('([^']+)'\)", expr)
        if includes_match:
            search_text = includes_match.group(1)
            return search_text in content

        # Handle MATCHES
        matches_match = re.match(r"MATCHES\('([^']+)'\)", expr)
        if matches_match:
            pattern = matches_match.group(1)
            return bool(re.search(pattern, content))

        raise ValueError(f"Invalid expression: {expr}")

    @staticmethod
    def validate_rule_syntax(rule: str) -> Dict[str, Any]:
        """Validate that a rule has correct syntax."""
        try:
            # Try to parse the rule
            PolicyEngine._validate_syntax_recursive(rule)
            return {"valid": True, "message": "Rule syntax is valid"}
        except Exception as e:
            return {"valid": False, "message": str(e)}

    @staticmethod
    def _validate_syntax_recursive(expr: str):
        """Recursively validate expression syntax."""
        expr = expr.strip()

        if not expr:
            raise ValueError("Empty expression")

        # Check for OR
        if " OR " in expr:
            parts = expr.split(" OR ")
            for part in parts:
                PolicyEngine._validate_syntax_recursive(part)
            return

        # Check for AND
        if " AND " in expr:
            parts = expr.split(" AND ")
            for part in parts:
                PolicyEngine._validate_syntax_recursive(part)
            return

        # Check for NOT
        if expr.startswith("NOT "):
            inner = expr[4:].strip()
            PolicyEngine._validate_syntax_recursive(inner)
            return

        # Check for INCLUDES
        if expr.startswith("INCLUDES("):
            if not re.match(r"INCLUDES\('([^']+)'\)", expr):
                raise ValueError(f"Invalid INCLUDES syntax: {expr}")
            return

        # Check for MATCHES
        if expr.startswith("MATCHES("):
            if not re.match(r"MATCHES\('([^']+)'\)", expr):
                raise ValueError(f"Invalid MATCHES syntax: {expr}")
            # Validate regex pattern
            match = re.match(r"MATCHES\('([^']+)'\)", expr)
            if match:
                pattern = match.group(1)
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {pattern} - {str(e)}")
            return

        raise ValueError(f"Unknown expression: {expr}")
