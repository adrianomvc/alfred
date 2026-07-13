from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, Sequence


AppendEvents = Callable[[str, Sequence[Mapping[str, object]]], None]
CursorWriter = Callable[[str, str, int, object], None]
PolicySnapshotWriter = Callable[[Mapping[str, object], Mapping[str, object]], None]


class RawHookAdapter(Protocol):
    def read_slice(self, transcript_path: str, cursor_path: str) -> tuple[list[str], int, int]: ...

    def normalize_records(self, lines: Sequence[str], provider: str) -> tuple[list[dict[str, object]], object]: ...


@dataclass(frozen=True)
class EngineInvocation:
    args: tuple[str, ...]


@dataclass(frozen=True)
class EngineRunResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


EngineRunner = Callable[[EngineInvocation], EngineRunResult]


@dataclass(frozen=True)
class ClaudeHookContext:
    transcript_path: str
    mode: str
    raw_log: str
    raw_cursor_path: str
    alfred_cursor_path: str
    state_path: str
    obs_log: str
    run_id: str
    provider: str
    project: str | None = None
    team: str | None = None
    environment: str | None = None


@dataclass(frozen=True)
class ProcessClaudeHookCommand:
    payload: Mapping[str, object]
    active: Mapping[str, object]
    context: ClaudeHookContext


@dataclass(frozen=True)
class ProcessClaudeHookResult:
    messages: tuple[str, ...] = ()


class ProcessClaudeHook:
    def __init__(
        self,
        *,
        raw_adapter: RawHookAdapter,
        append_events: AppendEvents,
        write_cursor: CursorWriter,
        write_policy_snapshot: PolicySnapshotWriter,
        run_engine: EngineRunner,
    ) -> None:
        self._raw_adapter = raw_adapter
        self._append_events = append_events
        self._write_cursor = write_cursor
        self._write_policy_snapshot = write_policy_snapshot
        self._run_engine = run_engine

    def execute(self, command: ProcessClaudeHookCommand) -> ProcessClaudeHookResult:
        messages = []
        context = command.context
        if context.mode in ("raw", "both") and context.raw_log:
            message = self._process_raw(context)
            if message:
                messages.append(message)
        if context.mode in ("alfred", "both"):
            messages.extend(self._process_alfred(command.payload, command.active, context))
        return ProcessClaudeHookResult(tuple(messages))

    def _process_raw(self, context: ClaudeHookContext) -> str | None:
        try:
            lines, _start_offset, end_offset = self._raw_adapter.read_slice(
                context.transcript_path,
                context.raw_cursor_path,
            )
            events, last_request_id = self._raw_adapter.normalize_records(lines, context.provider)
            for event in events:
                event["project"] = context.project
                event["team"] = context.team
                event["environment"] = context.environment
            self._append_events(context.raw_log, events)
            self._write_cursor(context.raw_cursor_path, context.transcript_path, end_offset, last_request_id)
        except Exception as error:  # noqa: BLE001 - hook must never block host
            return f"alfred-usage-hook raw: {error}"
        return None

    def _process_alfred(
        self,
        payload: Mapping[str, object],
        active: Mapping[str, object],
        context: ClaudeHookContext,
    ) -> list[str]:
        try:
            self._write_policy_snapshot(payload, active)
            invocation = self._engine_invocation(payload, context)
            if invocation is None:
                return [
                    "alfred-usage-hook: set ALFRED_STATE_PATH/ALFRED_OBS_LOG or render toolbar with -RegisterActive; skipping Alfred log"
                ]
            result = self._run_engine(invocation)
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip()
                return [f"alfred-usage-hook: {detail}"]
        except Exception as error:  # noqa: BLE001 - hook must never block host
            return [f"alfred-usage-hook alfred: {error}"]
        return []

    def _engine_invocation(self, payload: Mapping[str, object], context: ClaudeHookContext) -> EngineInvocation | None:
        if not context.state_path and not context.obs_log:
            return None

        args = [
            "--transcript-path",
            context.transcript_path,
            "--granularity",
            "request",
            "--emit-interactions",
            "--cursor-path",
            context.alfred_cursor_path,
        ]
        if context.state_path:
            args += ["--state-path", context.state_path]
        if context.obs_log:
            args += ["--output-path", context.obs_log]
        session_id = payload.get("session_id") or payload.get("sessionId")
        if session_id:
            args += ["--session-id", str(session_id)]
        if context.run_id:
            args += ["--run-id", context.run_id]
        return EngineInvocation(tuple(args))
