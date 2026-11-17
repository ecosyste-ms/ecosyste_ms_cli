"""Shared wiring for PURL options on auto-generated commands.

Several APIs accept a Package URL as a shorthand for the registry/ecosystem,
package, and (sometimes) version parameters a command already takes.
``attach_purl_option`` is the single mechanism for that: it makes the relevant
positional arguments optional, injects ``--purl``, and wraps the command's
callback so the PURL fills in any target the user didn't pass explicitly
(explicit values always win).

Options that send PURLs to the API as given (``PASS_THROUGH_PURL_FIELDS``) get
the ``PURL`` type instead, applied by the command generator.
"""

from typing import Optional, Sequence

import click

from ecosystems_cli.helpers.purl_parser import apply_purl, normalize_purl, purl_type_to_registry

# The PURL components, in the order they map onto a command's target parameters.
_PURL_COMPONENTS = ("ecosystem", "package_name", "version")


class PurlParamType(click.ParamType):
    """A PURL option value, validated and normalized to its canonical form."""

    name = "purl"

    def convert(self, value, param, ctx):
        try:
            return normalize_purl(value)
        except ValueError as e:
            self.fail(str(e), param, ctx)


PURL = PurlParamType()


def use_purl_type(command: click.Command, option_name: str) -> None:
    """Give a command's pass-through PURL option the ``PURL`` type.

    A malformed PURL then fails as a usage error before any request, and each
    value is sent in canonical form. Works for repeatable options too: each
    value is converted.
    """
    for param in command.params:
        if isinstance(param, click.Option) and param.name == option_name:
            param.type = PURL


def attach_purl_option(
    group: click.Group,
    command_name: str,
    *,
    targets: Sequence[str],
    with_version: bool = False,
    map_types: bool = True,
    error: Optional[str] = None,
    example: str,
) -> None:
    """Attach an optional ``--purl`` to an auto-generated command.

    Args:
        group: The Click group owning the command.
        command_name: Name of the auto-generated command to augment.
        targets: Command parameter names that the PURL decomposes into, paired
            positionally with ``_PURL_COMPONENTS`` (ecosystem, package_name,
            version). Any positional arguments among them are made optional;
            option-based targets are filled by name.
        with_version: Whether to also extract the version from the PURL.
        map_types: Map the PURL type to a registry name (e.g. ``npm`` ->
            ``npmjs.org``). Disable when the command filters by ecosystem name.
        error: Message raised as a ``UsageError`` when a target is still unset
            after decomposition. When ``None`` the PURL is an optional shortcut.
        example: Example PURL shown in the option help text.
    """
    if command_name not in group.commands:
        return

    cmd = group.commands[command_name]

    # Let --purl stand in for the positional arguments it decomposes into.
    for param in cmd.params:
        if isinstance(param, click.Argument) and param.name in targets:
            param.required = False

    # Normalize positional order to `targets` (e.g. REGISTRY_NAME before
    # PACKAGE_NAME) so every PURL-enabled command shares one contract that
    # matches the help text, regardless of the auto-generated argument order.
    arg_slots = [i for i, p in enumerate(cmd.params) if isinstance(p, click.Argument) and p.name in targets]
    ordered_args = sorted((cmd.params[i] for i in arg_slots), key=lambda p: list(targets).index(p.name))
    for slot, arg in zip(arg_slots, ordered_args):
        cmd.params[slot] = arg

    cmd.params.insert(
        0,
        click.Option(["--purl"], type=str, default=None, help=f"Package URL (PURL). Example: {example}"),
    )

    original_callback = cmd.callback
    type_mapper = purl_type_to_registry if map_types else (lambda purl_type: purl_type)

    def wrapped_callback(*args, **kwargs):
        parsed = apply_purl(kwargs.pop("purl", None), with_version=with_version, type_mapper=type_mapper)
        for component, target in zip(_PURL_COMPONENTS, targets):
            if not kwargs.get(target):
                kwargs[target] = parsed.get(component)
        if error and any(not kwargs.get(target) for target in targets):
            raise click.UsageError(error)
        return original_callback(*args, **kwargs)

    cmd.callback = wrapped_callback
