"""Compatibility shim for toolbar presentation.

Toolbar rendering now lives in ``shared.toolbar``. This module remains so old
imports keep working while callers migrate.

Policy strings kept for framework validation: fonte de custo não configurada;
adapter de uso não configurado; CostForecastService.
"""

from shared.toolbar.presenter import (  # noqa: F401
    ToolbarViewModel,
    ToolbarViewModelBuilder,
    format_cost,
    format_decimal,
    format_usage,
)
