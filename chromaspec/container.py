"""
Dependency injection container for ChromaSpec.

This module provides a simple dependency injection container to improve
testability and reduce coupling between modules.
"""

from typing import Any, Callable, Dict


class ServiceContainer:
    """Simple service container for dependency injection."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}

    def register(self, name: str, factory: Callable) -> None:
        """Register a service factory."""
        self._factories[name] = factory

    def register_instance(self, name: str, instance: Any) -> None:
        """Register a service instance (singleton)."""
        self._services[name] = instance

    def get(self, name: str) -> Any:
        """Get a service instance."""
        if name not in self._services:
            if name in self._factories:
                self._services[name] = self._factories[name]()
            else:
                raise KeyError(f"Service '{name}' not registered")
        return self._services[name]

    def clear(self) -> None:
        """Clear all services (useful for testing)."""
        self._services.clear()
        self._factories.clear()


# Global container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return _container


def configure_container() -> None:
    """Configure default services."""
    from chromaspec.analyzers.classification import categorize_colors
    from chromaspec.extractors.image_extractor import extract_colors_from_image
    from chromaspec.extractors.svg_extractor import extract_colors_from_svg

    container = get_container()
    container.register("image_extractor", lambda: extract_colors_from_image)
    container.register("svg_extractor", lambda: extract_colors_from_svg)
    container.register("color_categorizer", lambda: categorize_colors)
