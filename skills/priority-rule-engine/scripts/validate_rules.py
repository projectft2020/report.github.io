#!/usr/bin/env python3
"""
Validate Priority Rules Configuration

Check rules configuration for errors.
"""

import sys
import json
from pathlib import Path
import argparse

DEFAULT_RULES_FILE = Path(__file__).parent.parent / "references" / "priority_rules.json"

PRIORITY_VALUES = ["high", "medium", "normal", "low"]
REQUIRED_FIELDS = ["name", "description", "condition", "action", "priority"]

def validate_rules(rules_path=None):
    """Validate rules configuration file.

    Returns:
        Tuple of (is_valid, errors)
    """
    if rules_path is None:
        rules_path = DEFAULT_RULES_FILE

    if not rules_path.exists():
        print(f"❌ 規則文件不存在: {rules_path}")
        return False, ["規則文件不存在"]

    try:
        with open(rules_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ JSON 解析失敗: {e}")
        return False, ["JSON 解析失敗"]

    if not isinstance(data, list):
        return False, ["規則必須是數組格式"]

    errors = []

    for i, rule in enumerate(data, 1):
        rule_errors = validate_single_rule(rule, i)
        errors.extend(rule_errors)

    return len(errors) == 0, errors

def validate_single_rule(rule, index):
    """Validate a single rule object.

    Returns:
        List of error messages for this rule
    """
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in rule:
            errors.append(f"規則 {index}: 缺少必填字段 '{field}'")

    # Validate priority value
    if "priority" in rule:
        if rule["priority"] not in PRIORITY_VALUES:
            errors.append(
                f"規則 {index}: 無效的優先級 '{rule['priority']}' "
                f"(必須是: {', '.join(PRIORITY_VALUES)})"
            )

    # Validate action
    if "action" in rule and rule["action"] != "set_priority":
        errors.append(
            f"規則 {index}: 無效的操作 '{rule['action']}' "
            "(目前只支持: set_priority)"
        )

    # Validate condition structure
    if "condition" in rule:
        condition = rule["condition"]
        condition_errors = validate_condition(condition, index)
        errors.extend(condition_errors)

    return errors

def validate_condition(condition, rule_index):
    """Validate rule condition object.

    Returns:
        List of error messages
    """
    errors = []

    if not isinstance(condition, dict):
        errors.append(f"規則 {rule_index}: condition 必須是對象")
        return errors

    # Validate status
    if "status" in condition:
        if condition["status"] not in ["pending", "in_progress", "completed", "failed"]:
            errors.append(
                f"規則 {rule_index}: 無效的 status '{condition['status']}'"
            )

    # Validate current_priority
    if "current_priority" in condition:
        if not isinstance(condition["current_priority"], list):
            errors.append(
                f"規則 {rule_index}: current_priority 必須是數組"
            )
        else:
            for prio in condition["current_priority"]:
                if prio not in PRIORITY_VALUES:
                    errors.append(
                        f"規則 {rule_index}: 無效的優先級 '{prio}' "
                        f"在 current_priority 中"
                    )

    # Validate days_pending operator
    if "days_pending" in condition:
        days_str = str(condition["days_pending"])
        valid_ops = [">", "<", ">=", "<="]
        if not any(days_str.startswith(op) for op in valid_ops):
            errors.append(
                f"規則 {rule_index}: days_pending 必須以 "
                f"{', '.join(valid_ops)} 開頭"
            )

    # Validate tags
    if "tags" in condition:
        if not isinstance(condition["tags"], list):
            errors.append(f"規則 {rule_index}: tags 必須是數組")
        elif len(condition["tags"]) == 0:
            errors.append(f"規則 {rule_index}: tags 不能為空")

    # Validate keywords
    if "keywords" in condition:
        if not isinstance(condition["keywords"], list):
            errors.append(f"規則 {rule_index}: keywords 必須是數組")
        elif len(condition["keywords"]) == 0:
            errors.append(f"規則 {rule_index}: keywords 不能為空")

    # Validate related_score operator
    if "related_score" in condition:
        score_str = str(condition["related_score"])
        valid_ops = [">", "<", ">=", "<="]
        if not any(score_str.startswith(op) for op in valid_ops):
            errors.append(
                f"規則 {rule_index}: related_score 必須以 "
                f"{', '.join(valid_ops)} 開頭"
            )

    return errors

def display_validation_result(is_valid, errors):
    """Display validation results."""
    print("=" * 60)
    print("🔍 優先級規則驗證")
    print("=" * 60)
    print()

    if is_valid:
        print("✅ 所有規則驗證通過")
        print()
        print("規則配置有效，可以安全應用。")
    else:
        print(f"❌ 發現 {len(errors)} 個錯誤:")
        print()

        for error in errors:
            print(f"  - {error}")

        print()
        print("💡 請修正上述錯誤後重新運行驗證")

    print()
    print("=" * 60)

    return is_valid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate priority rules")
    parser.add_argument(
        "rules_path",
        nargs="?",
        help="Path to rules configuration file (default: references/priority_rules.json)"
    )
    args = parser.parse_args()

    is_valid, errors = validate_rules(args.rules_path)
    display_validation_result(is_valid, errors)

    sys.exit(0 if is_valid else 1)
