"""
    Definition for error hierarchy
"""


class BasicValueError(ValueError):
    pass


class ReturnResultValueLessThanOne(BasicValueError):
    pass
