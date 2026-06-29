from enum import StrEnum


class FeatureFlagScope(StrEnum):
    GLOBAL = "GLOBAL"
    MODULE = "MODULE"
    USER = "USER"
