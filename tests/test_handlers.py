"""Tests for operation handlers and the handler factory."""

from ecosystems_cli.commands.handlers import (
    DefaultOperationHandler,
    OperationHandlerFactory,
    PackagesOperationHandler,
)


class TestOperationHandlerFactory:
    """How the factory resolves handlers per API."""

    def test_registered_api_gets_dedicated_handler(self):
        assert isinstance(OperationHandlerFactory.get_handler("packages"), PackagesOperationHandler)

    def test_unregistered_api_falls_back_to_default(self):
        assert isinstance(OperationHandlerFactory.get_handler("does-not-exist"), DefaultOperationHandler)


class TestDefaultOperationHandlerFallback:
    """The fallback maps everything to query params with no path params."""

    def setup_method(self):
        self.handler = DefaultOperationHandler()

    def test_all_kwargs_become_query_params(self):
        path_params, query_params = self.handler.build_params("anyOperation", (), {"page": 1, "per_page": 20})
        assert path_params == {}
        assert query_params == {"page": 1, "per_page": 20}

    def test_none_values_are_dropped(self):
        path_params, query_params = self.handler.build_params("anyOperation", (), {"page": 1, "label": None})
        assert path_params == {}
        assert query_params == {"page": 1}

    def test_no_params_returns_empty(self):
        assert self.handler.build_params("anyOperation", (), {}) == ({}, {})


class TestBaseHandlerParamMapping:
    """The OPERATION_PARAMS contract a real handler relies on."""

    def setup_method(self):
        self.handler = PackagesOperationHandler()

    def test_positional_args_fill_path_params_in_order(self):
        path_params, query_params = self.handler.build_params("getRegistryPackage", ("npmjs.org", "lodash"), {})
        assert path_params == {"registryName": "npmjs.org", "packageName": "lodash"}
        assert query_params == {}

    def test_lowercase_kwarg_variants_map_to_path_params(self):
        # Click lowercases argument names; the handler accepts those variants.
        path_params, query_params = self.handler.build_params(
            "getRegistryPackage", (), {"registryname": "npmjs.org", "packagename": "lodash", "page": 2}
        )
        assert path_params == {"registryName": "npmjs.org", "packageName": "lodash"}
        assert query_params == {"page": 2}
