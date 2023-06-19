from os import environ
from unittest import TestCase

from integration.resources.abstract_class_dependencies_classes import (
    AbstractBaseClass,
    AbstractBaseClassFirstChildren,
    AbstractBaseClassSecondChildren,
    ClassWithAbstractClassDependencies,
)
from integration.resources.class_with_configuration_values import ClassWithConfigurationValues
from integration.resources.iterable_dependencies_classes import (
    ClassWithIterableDependencies,
    FirstIterableDependencyClass,
    SecondIterableDependencyClass,
)
from integration.resources.keyword_dependencies_classes import (
    ClassWithKeywordDependencies,
    KeywordDependencyClass,
    keyword_dependency_class_default_instance,
)
from integration.resources.optional_dependencies_classes import ClassWithOptionalDependencies, OptionalDependencyClass
from integration.resources.primary_dependencies_classes import (
    ClassWithPrimaryDependencies,
    PrimaryDependencyBaseClass,
    PrimaryDependencyFirstChildren,
    PrimaryDependencySecondChildren,
)
from integration.resources.simple_dependency_classes import SimpleDependencyClass, SimpleDependencyDependencyClass

from yadil.configuration.configuration_container import ConfigurationContainer
from yadil.configuration.environment import Environment
from yadil.container import Container
from yadil.errors.abstract_class_not_allowed_error import AbstractClassNotAllowedError
from yadil.errors.dependency_not_found_error import DependencyNotFoundError
from yadil.errors.missing_configuration_value_error import MissingConfigurationValueError
from yadil.errors.primary_dependency_already_defined_error import PrimaryDependencyAlreadyDefinedError


class TestContainer(TestCase):
    def setUp(self) -> None:
        self.configuration_container = ConfigurationContainer()
        self.container = Container(self.configuration_container)

    def test_add_class(self):
        self.container.add(SimpleDependencyDependencyClass)

        simple_dependency_dependency_class = self.container[SimpleDependencyDependencyClass]
        self.assertIsInstance(simple_dependency_dependency_class, SimpleDependencyDependencyClass)

    def test_add_instance(self):
        simple_dependency_dependency_class_instance = SimpleDependencyDependencyClass()

        self.container[SimpleDependencyDependencyClass] = simple_dependency_dependency_class_instance

        result_simple_dependency_dependency_class = self.container[SimpleDependencyDependencyClass]
        self.assertEqual(simple_dependency_dependency_class_instance, result_simple_dependency_dependency_class)

    def test_add_abstract_class(self):
        with self.assertRaises(AbstractClassNotAllowedError) as context:
            self.container.add(AbstractBaseClass)

        self.assertEqual(AbstractBaseClass, context.exception.abstract_class)

    def test_add_instance_abstract_class(self):
        abstract_class_instance = AbstractBaseClassFirstChildren()
        self.container.add(AbstractBaseClassSecondChildren)

        self.container[AbstractBaseClass] = abstract_class_instance

        result_abstract_class_instance = self.container[AbstractBaseClass]
        self.assertEqual(abstract_class_instance, result_abstract_class_instance)
        abstract_class_second_children_instance = self.container[AbstractBaseClassSecondChildren]
        self.assertIsInstance(abstract_class_second_children_instance, AbstractBaseClassSecondChildren)

    def test_add_multiple_primaries(self):
        self.container.add(PrimaryDependencyFirstChildren, is_primary=True)

        with self.assertRaises(PrimaryDependencyAlreadyDefinedError) as context:
            self.container.add(PrimaryDependencySecondChildren, is_primary=True)

        self.assertEqual(PrimaryDependencyBaseClass, context.exception.base_class)

    def test_get_class_with_dependencies(self):
        self.container.add(SimpleDependencyClass)
        self.container.add(SimpleDependencyDependencyClass)

        simple_dependency_class = self.container[SimpleDependencyClass]

        self.assertIsInstance(simple_dependency_class, SimpleDependencyClass)
        self.assertIsNotNone(simple_dependency_class.dependency)
        self.assertIsInstance(simple_dependency_class.dependency, SimpleDependencyDependencyClass)

    def test_get_class_without_required_dependencies(self):
        self.container.add(SimpleDependencyClass)

        with self.assertRaises(DependencyNotFoundError) as context:
            _ = self.container[SimpleDependencyClass]

        self.assertEqual(SimpleDependencyDependencyClass, context.exception.dependency_type)

    def test_get_class_missing_optional_dependency(self):
        self.container.add(ClassWithOptionalDependencies)

        class_with_optional_dependencies = self.container[ClassWithOptionalDependencies]

        self.assertIsInstance(class_with_optional_dependencies, ClassWithOptionalDependencies)
        self.assertIsNone(class_with_optional_dependencies.optional_dependency)

    def test_get_class_with_abstract_dependency(self):
        self.container.add(ClassWithAbstractClassDependencies)
        self.container.add(AbstractBaseClassFirstChildren)

        class_with_abstract_class_dependencies = self.container[ClassWithAbstractClassDependencies]

        self.assertIsInstance(class_with_abstract_class_dependencies, ClassWithAbstractClassDependencies)
        self.assertIsNotNone(class_with_abstract_class_dependencies.abstract_class_dependencies)
        self.assertIsInstance(
            class_with_abstract_class_dependencies.abstract_class_dependencies, AbstractBaseClassFirstChildren
        )

    def test_get_class_with_optional_dependency(self):
        self.container.add(ClassWithOptionalDependencies)
        self.container.add(OptionalDependencyClass)

        class_with_optional_dependencies = self.container[ClassWithOptionalDependencies]

        self.assertIsInstance(class_with_optional_dependencies, ClassWithOptionalDependencies)
        self.assertIsNotNone(class_with_optional_dependencies.optional_dependency)
        self.assertIsInstance(class_with_optional_dependencies.optional_dependency, OptionalDependencyClass)

    def test_get_class_with_keyword_dependency_missing(self):
        self.container.add(ClassWithKeywordDependencies)

        class_with_keyword_dependencies = self.container[ClassWithKeywordDependencies]

        self.assertIsInstance(class_with_keyword_dependencies, ClassWithKeywordDependencies)
        self.assertEqual(keyword_dependency_class_default_instance, class_with_keyword_dependencies.keyword_dependency)

    def test_get_class_with_keyword_dependencies_specified(self):
        self.container.add(ClassWithKeywordDependencies)
        self.container.add(KeywordDependencyClass)

        class_with_keyword_dependencies = self.container[ClassWithKeywordDependencies]

        self.assertIsInstance(class_with_keyword_dependencies, ClassWithKeywordDependencies)
        self.assertNotEqual(
            keyword_dependency_class_default_instance, class_with_keyword_dependencies.keyword_dependency
        )
        self.assertIsInstance(class_with_keyword_dependencies.keyword_dependency, KeywordDependencyClass)

    def test_get_class_with_iterable_dependencies(self):
        self.container.add(ClassWithIterableDependencies)
        self.container.add(FirstIterableDependencyClass)
        self.container.add(SecondIterableDependencyClass)

        class_with_iterable_dependencies = self.container[ClassWithIterableDependencies]

        self.assertIsInstance(class_with_iterable_dependencies, ClassWithIterableDependencies)
        self.assertIsNotNone(class_with_iterable_dependencies.iterable_dependencies)
        self.assertIsInstance(class_with_iterable_dependencies.iterable_dependencies, set)
        for iterable_dependency in class_with_iterable_dependencies.iterable_dependencies:
            self.assertTrue(
                isinstance(iterable_dependency, FirstIterableDependencyClass)
                or isinstance(iterable_dependency, SecondIterableDependencyClass)
            )

    def test_get_class_with_primary_defined(self):
        self.container.add(ClassWithPrimaryDependencies)
        self.container.add(PrimaryDependencyFirstChildren)
        self.container.add(PrimaryDependencySecondChildren, is_primary=True)

        class_with_primary_dependencies = self.container[ClassWithPrimaryDependencies]

        self.assertIsInstance(class_with_primary_dependencies, ClassWithPrimaryDependencies)
        self.assertIsNotNone(class_with_primary_dependencies.primary_dependency)
        self.assertIsInstance(class_with_primary_dependencies.primary_dependency, PrimaryDependencySecondChildren)

    def test_get_class_with_configuration_values(self):
        self.configuration_container["value1"] = "value1"
        self.configuration_container["value2"] = 12
        self.container.add(ClassWithConfigurationValues)

        class_with_configuration_values = self.container[ClassWithConfigurationValues]

        self.assertIsInstance(class_with_configuration_values, ClassWithConfigurationValues)
        self.assertEqual(class_with_configuration_values.value1, "value1")
        self.assertEqual(class_with_configuration_values.value2, 12)

    def test_get_class_with_configuration_values_missing(self):
        self.container.add(ClassWithConfigurationValues)

        with self.assertRaises(MissingConfigurationValueError) as context:
            _ = self.container[ClassWithConfigurationValues]

        self.assertEqual("value1", context.exception.configuration_value_name)

    def test_get_class_with_configuration_values_from_environment(self):
        environ["YADIL_TEST_VALUE1"] = "value1"
        environ["YADIL_TEST_VALUE2"] = "12"
        self.container.add(ClassWithConfigurationValues)
        self.configuration_container["value1"] = Environment("YADIL_TEST_VALUE1")
        self.configuration_container["value2"] = Environment("YADIL_TEST_VALUE2")

        class_with_configuration_values = self.container[ClassWithConfigurationValues]

        self.assertIsInstance(class_with_configuration_values, ClassWithConfigurationValues)
        self.assertEqual(class_with_configuration_values.value1, "value1")
        self.assertEqual(class_with_configuration_values.value2, 12)

        del environ["YADIL_TEST_VALUE1"]
        del environ["YADIL_TEST_VALUE2"]
