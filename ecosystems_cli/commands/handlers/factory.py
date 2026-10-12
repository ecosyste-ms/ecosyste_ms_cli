"""Factory for creating operation handlers."""

from typing import Dict, Type

from .advisories import AdvisoriesOperationHandler
from .archives import ArchivesOperationHandler
from .awesome import AwesomeOperationHandler
from .base import OperationHandler
from .commits import CommitsOperationHandler
from .default import DefaultOperationHandler
from .dependabot import DependabotOperationHandler
from .diff import DiffOperationHandler
from .docker import DockerOperationHandler
from .issues import IssuesOperationHandler
from .licenses import LicensesOperationHandler
from .opencollective import OpenCollectiveOperationHandler
from .packages import PackagesOperationHandler
from .parser import ParserOperationHandler
from .repos import ReposOperationHandler
from .resolve import ResolveOperationHandler
from .sbom import SbomOperationHandler
from .sponsors import SponsorsOperationHandler
from .summary import SummaryOperationHandler
from .timeline import TimelineOperationHandler


class OperationHandlerFactory:
    """Factory for creating operation handlers."""

    _handlers: Dict[str, Type[OperationHandler]] = {
        "advisories": AdvisoriesOperationHandler,
        "archives": ArchivesOperationHandler,
        "awesome": AwesomeOperationHandler,
        "commits": CommitsOperationHandler,
        "dependabot": DependabotOperationHandler,
        "diff": DiffOperationHandler,
        "docker": DockerOperationHandler,
        "issues": IssuesOperationHandler,
        "licenses": LicensesOperationHandler,
        "opencollective": OpenCollectiveOperationHandler,
        "packages": PackagesOperationHandler,
        "parser": ParserOperationHandler,
        "repos": ReposOperationHandler,
        "resolve": ResolveOperationHandler,
        "sbom": SbomOperationHandler,
        "sponsors": SponsorsOperationHandler,
        "summary": SummaryOperationHandler,
        "timeline": TimelineOperationHandler,
    }

    @classmethod
    def get_handler(cls, api_name: str) -> OperationHandler:
        """Get the appropriate handler for an API.

        Args:
            api_name: Name of the API

        Returns:
            OperationHandler instance for the API
        """
        handler_class = cls._handlers.get(api_name, DefaultOperationHandler)
        return handler_class()
