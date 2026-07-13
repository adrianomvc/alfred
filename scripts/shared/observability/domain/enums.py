from enum import Enum


class Confidence(str, Enum):
    EXACT = "exact"
    RATED = "rated"
    ESTIMATED = "estimated"
    ALLOCATED = "allocated"
    MANUAL = "manual"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


class CostScope(str, Enum):
    REQUEST = "request"
    INTERACTION = "interaction"
    SESSION = "session"
    DEMAND = "demand"
    INITIATIVE = "initiative"
    ORGANIZATION = "organization"


class EventScope(str, Enum):
    REQUEST = "request"
    INTERACTION = "interaction"
    STEP = "step"
    SESSION = "session"


class EventType(str, Enum):
    USAGE_ATTRIBUTED = "usage_attributed"
    USAGE_COST_ATTRIBUTED = "usage_cost_attributed"
    INTERACTION_COMPLETED = "interaction_completed"
    ARTIFACT_ACCESSED = "artifact_accessed"
    ARTIFACT_CHANGED = "artifact_changed"
    POLICY_SNAPSHOT = "policy_snapshot"


class UsageUnit(str, Enum):
    TOKEN_INPUT = "token.input"
    TOKEN_OUTPUT = "token.output"
    TOKEN_CACHE_CREATION = "token.cache_creation"
    TOKEN_CACHE_READ = "token.cache_read"
    ACU = "acu"
    ACU_DEVIN = "acu.devin"
    ACU_TERMINAL = "acu.terminal"
    ACU_REVIEW = "acu.review"
    CREDIT = "credit"
    REQUEST = "request"
    MINUTE = "minute"
    CUSTOM = "custom"


class ArtifactOperation(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SNAPSHOT = "snapshot"
    REFERENCE = "reference"

