from typing import Any, Dict, Optional, Type, get_type_hints

from yandil.container import Container, default_container
from yandil.errors.dependency_not_found_error import DependencyNotFoundError


class DependencyFiller:
    def __init__(self, container: Optional[Container] = None):
        if container is None:
            container = default_container
        self.__dependencies_container = container

    def fill(self, target_class: Type) -> None:
        target_class_base_init = target_class.__init__
        dependencies = self.__get_target_class_dependencies(target_class)

        def init_with_dependencies(target_self, *args, **kwargs) -> None:
            target_class_base_init(target_self, *args, **kwargs, **dependencies)

        target_class.__init__ = init_with_dependencies

    def __get_target_class_dependencies(self, target_class: Type) -> Dict[str, Any]:
        dependencies_dict = {}
        for argument_name, argument_type in get_type_hints(target_class.__init__).items():
            try:
                dependencies_dict[argument_name] = self.__dependencies_container[argument_type]
            except DependencyNotFoundError:
                pass
        return dependencies_dict
