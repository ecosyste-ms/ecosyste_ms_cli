"""Operation handlers for different API types."""

from .advisories import AdvisoriesOperationHandler
from .archives import ArchivesOperationHandler
from .awesome import AwesomeOperationHandler
from .base import OperationHandler
from .commits import CommitsOperationHandler
from .default import DefaultOperationHandler
from .dependabot import DependabotOperationHandler
from .diff import DiffOperationHandler
from .docker import DockerOperationHandler
from .factory import OperationHandlerFactory
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

__all__ = [
    "AdvisoriesOperationHandler",
    "ArchivesOperationHandler",
    "AwesomeOperationHandler",
    "CommitsOperationHandler",
    "DefaultOperationHandler",
    "DependabotOperationHandler",
    "DiffOperationHandler",
    "DockerOperationHandler",
    "IssuesOperationHandler",
    "LicensesOperationHandler",
    "OpenCollectiveOperationHandler",
    "OperationHandler",
    "OperationHandlerFactory",
    "PackagesOperationHandler",
    "ParserOperationHandler",
    "ReposOperationHandler",
    "ResolveOperationHandler",
    "SbomOperationHandler",
    "SponsorsOperationHandler",
    "SummaryOperationHandler",
    "TimelineOperationHandler",
]
