# from abc import ABC, abstractmethod
# from typing import final, override, Final
# from value import Value
#
#
# class NamedMemory(ABC):
#     @property
#     @abstractmethod
#     def name(self) -> str:
#         pass
#
#     @abstractmethod
#     def raise_if_not_assignable(self, value: Value) -> None:
#         pass
#
#     @abstractmethod
#     def __str__(self) -> str:
#         pass
#
#
# @final
# class VariableName(NamedMemory):
#     def __init__(self, name: str, type_: type) -> None:
#         self._name = name
#         self._type = type_
#
#     @override
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @override
#     def raise_if_not_assignable(self, value: Value) -> None:
#         if not isinstance(value, self._type):
#             msg: Final = (
#                 f"Value of type '{type(value).__name__}' cannot be assigned to "
#                 + f"variable '{self._name}' of type '{self._type.__name__}'."
#             )
#             raise TypeError(msg)
#
#     @override
#     def __str__(self) -> str:
#         return f"VariableName(name={self._name}, type={self._type.__name__})"
