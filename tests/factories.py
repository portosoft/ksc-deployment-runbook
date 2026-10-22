"""
Factory functions for building CheckResult and CheckItem test objects.

Provides helpers to construct test fixtures without hardcoded status strings
or messages scattered across test files.
"""
from automation.python.checks import CheckItem, CheckResult


def make_check_item(name: str, status: str = "ok", message: str = "") -> CheckItem:
    """Return a CheckItem with the given fields.

    Args:
        name: Identifier for the check item.
        status: One of ``"ok"``, ``"warning"``, or ``"critical"`` (any string accepted).
        message: Human-readable detail for the item.

    Returns:
        A :class:`CheckItem` instance populated with the supplied parameters.
    """
    return CheckItem(name=name, status=status, message=message)


def make_check_result(items=None) -> CheckResult:
    """Return a CheckResult wrapping the given list of items.

    Args:
        items: List of :class:`CheckItem` instances.  Defaults to an empty list
               when ``None`` is passed.

    Returns:
        A :class:`CheckResult` instance whose ``items`` field equals the
        provided list, or ``[]`` when *items* is ``None``.
    """
    return CheckResult(items=items if items is not None else [])


def make_critical_result(
    name: str = "test_crit",
    message: str = "Falha de teste",
) -> CheckResult:
    """Return a CheckResult containing exactly one critical CheckItem.

    Args:
        name: The ``name`` field of the single contained :class:`CheckItem`.
        message: The ``message`` field of the single contained :class:`CheckItem`.

    Returns:
        A :class:`CheckResult` with a single :class:`CheckItem` where
        ``status == "critical"``.
    """
    item = CheckItem(name=name, status="critical", message=message)
    return CheckResult(items=[item])
