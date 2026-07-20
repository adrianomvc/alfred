from pathlib import Path

from shared.common import read_lines
from shared.model_policy import describe_model
from shared.toolbar.presenter import ToolbarViewModelBuilder
from shared.toolbar.renderers import render_rich, render_text, render_web
from shared.toolbar.runtime import read_app_commit, resolve_framework_display
from shared.toolbar.state import parse_toolbar_state
from shared.toolbar.summary import build_toolbar_summary


def render_toolbar(
    state_path,
    *,
    framework_root,
    model="default",
    cost="n/a",
    profile="rich",
    cost_usd="",
    app_commit="",
    app_demand_path="",
    write_usage_summary=False,
):
    state = Path(state_path)
    if not state.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")

    content = read_lines(state)
    toolbar_state = parse_toolbar_state(content)
    # Always show the model actually running (passed via --model, else the state
    # `model` field); the policy target is shown only as guidance and flagged when
    # it differs. Never present the policy target as if it were running (D3).
    actual_model = model if model and model != "default" else toolbar_state.model
    described = describe_model(actual_model, toolbar_state.lane, toolbar_state.phase,
                               host=toolbar_state.host)
    model = described if described else model
    framework = resolve_framework_display(
        framework_root,
        toolbar_state.framework_version,
        toolbar_state.framework_commit,
    )
    app_commit_display = read_app_commit(state, content, app_commit, app_demand_path)
    summary = build_toolbar_summary(
        state,
        toolbar_state,
        cost=cost,
        cost_usd=cost_usd,
        write_usage_summary=write_usage_summary,
    )
    view_model = ToolbarViewModelBuilder().build(
        demand_id=toolbar_state.demand_id,
        sigla=toolbar_state.sigla,
        lane=toolbar_state.lane,
        progress=toolbar_state.progress,
        framework=framework,
        app_commit=app_commit_display,
        summary=summary,
        usage_fallback=toolbar_state.usage_acu_display,
    )

    if profile == "rich":
        return render_rich(
            toolbar_state.sigla, toolbar_state.demand_id, toolbar_state.lane,
            toolbar_state.phase, toolbar_state.next_step, toolbar_state.checkpoint,
            model, toolbar_state.progress, toolbar_state.markers, framework,
            app_commit_display, view_model,
        )
    if profile == "web":
        return render_web(
            toolbar_state.sigla, toolbar_state.demand_id, toolbar_state.lane,
            toolbar_state.next_step, toolbar_state.step, toolbar_state.progress,
            toolbar_state.markers,
        )

    return render_text(
        toolbar_state.sigla, toolbar_state.demand_id, toolbar_state.lane,
        toolbar_state.phase, toolbar_state.next_step, toolbar_state.step,
        toolbar_state.checkpoint, model, toolbar_state.progress,
        toolbar_state.markers, framework, app_commit_display, view_model,
    )
