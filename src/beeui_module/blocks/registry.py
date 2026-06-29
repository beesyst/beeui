from __future__ import annotations

import re
from typing import Any

from beeui_module.blocks.models import BlockDefinition, BlockPlacement, RenderedBlock
from beeui_module.blocks.renderers import (
    coerce_resolved_block,
    render_block,
    validate_block_definition,
)
from beeui_module.data.models import DataSourceDefinition
from beeui_module.data.resolver import DataResolver

_SAFE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")


def parse_blocks_registry(
    blocks_payload: Any,
    available_source_ids: set[str] | None = None,
) -> dict[str, BlockDefinition]:
    if not isinstance(blocks_payload, dict):
        raise ValueError("blocks must be a mapping")

    blocks: dict[str, BlockDefinition] = {}
    for block_id, block_payload in blocks_payload.items():
        if not isinstance(block_id, str) or not block_id.strip():
            raise ValueError("blocks keys must be non-empty strings")
        if not _SAFE_IDENTIFIER_RE.fullmatch(block_id):
            raise ValueError(f"blocks.{block_id} must be a safe identifier")
        blocks[block_id] = validate_block_definition(
            block_id,
            block_payload,
            available_source_ids=available_source_ids,
        )

    return blocks


def parse_page_block_placements(
    *,
    page_blocks: Any,
    page_index: int,
    available_block_ids: set[str],
) -> list[BlockPlacement]:
    if not isinstance(page_blocks, list):
        raise ValueError(f"pages[{page_index}].blocks must be a list")

    placements: list[BlockPlacement] = []
    for block_index, item in enumerate(page_blocks):
        if not isinstance(item, dict):
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}] must be a mapping"
            )

        keys = set(item)
        has_placement_keys = bool(keys & {"block", "width"})
        has_ref_keys = bool(keys & {"id", "enabled"})

        if has_placement_keys and has_ref_keys:
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}] must not mix placement keys (block, width) with reference keys (id, enabled)"
            )

        if has_ref_keys:
            _validate_page_block_ref(
                item,
                page_index=page_index,
                block_index=block_index,
                placements=placements,
            )
        else:
            _validate_block_placement(
                item,
                page_index=page_index,
                block_index=block_index,
                available_block_ids=available_block_ids,
                placements=placements,
            )

    return placements


def _validate_page_block_ref(
    item: dict[str, Any],
    *,
    page_index: int,
    block_index: int,
    placements: list[BlockPlacement],
) -> None:
    unknown_keys = sorted(set(item) - {"id", "enabled"})
    if unknown_keys:
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}] contains unsupported keys: {', '.join(unknown_keys)}"
        )

    block_id = item.get("id")
    if not isinstance(block_id, str) or not block_id.strip():
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}].id must be a non-empty string"
        )
    if not _SAFE_IDENTIFIER_RE.fullmatch(block_id):
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}].id must be a safe identifier"
        )

    enabled = item.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}].enabled must be a boolean"
        )

    if enabled:
        placements.append(BlockPlacement(block_id=block_id, width=12))


def _validate_block_placement(
    item: dict[str, Any],
    *,
    page_index: int,
    block_index: int,
    available_block_ids: set[str],
    placements: list[BlockPlacement],
) -> None:
    unknown_keys = sorted(set(item) - {"block", "width", "span", "size"})
    if unknown_keys:
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}] contains unsupported keys: {', '.join(unknown_keys)}"
        )

    block_id = item.get("block")
    if not isinstance(block_id, str) or not block_id.strip():
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}].block must be a non-empty string"
        )
    if block_id not in available_block_ids:
        raise ValueError(f"Unknown block reference: {block_id}")

    sizing_keys = {"width", "span", "size"}
    present = sizing_keys & set(item)
    if len(present) > 1:
        raise ValueError(
            f"pages[{page_index}].blocks[{block_index}] must not mix sizing keys: {', '.join(sorted(present))}"
        )

    width = item.get("width")
    if width is not None:
        if not isinstance(width, int) or width < 1 or width > 12:
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}].width must be an integer in range 1..12"
            )
        placements.append(BlockPlacement(block_id=block_id, width=width))
        return

    span = item.get("span")
    if span is not None:
        if not isinstance(span, int) or span < 1 or span > 12:
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}].span must be an integer in range 1..12"
            )
        placements.append(BlockPlacement(block_id=block_id, span=span))
        return

    size = item.get("size")
    if size is not None:
        if not isinstance(size, str) or size.upper() not in {"S", "M", "L", "XL"}:
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}].size must be one of S, M, L, XL"
            )
        placements.append(BlockPlacement(block_id=block_id, size=size.upper()))
        return

    placements.append(BlockPlacement(block_id=block_id, width=12))


_SIZE_TO_WIDTH: dict[str, int] = {"S": 4, "M": 6, "L": 8, "XL": 12}


def _resolve_placement_width(placement: BlockPlacement) -> int:
    if placement.span is not None:
        return placement.span
    if placement.size is not None:
        return _SIZE_TO_WIDTH.get(placement.size, 12)
    return placement.width


def resolve_page_blocks(
    *,
    placements: list[BlockPlacement],
    registry: dict[str, BlockDefinition],
    data_sources: dict[str, DataSourceDefinition] | None = None,
) -> list[RenderedBlock]:
    rendered: list[RenderedBlock] = []
    resolver = DataResolver(data_sources or {})
    for placement in placements:
        block = registry[placement.block_id]
        rendered.append(
            render_block(
                _resolve_block_definition(block, resolver),
                _resolve_placement_width(placement),
            )
        )
    return rendered


def _resolve_block_definition(
    block: BlockDefinition,
    resolver: DataResolver,
) -> BlockDefinition:
    if block.source_id is None or not block.bindings:
        return block

    resolved_values: dict[str, Any] = {}
    resolution_status = "ok"
    warning_messages: list[str] = []

    for field_name, selector in block.bindings.items():
        envelope = resolver.resolve(block.source_id, selector)
        if envelope.status == "ok":
            resolved_values[field_name] = envelope.data
            continue

        resolution_status = _merge_resolution_status(
            resolution_status,
            envelope.status,
        )
        warning_messages.extend(warning.message for warning in envelope.warnings)

    message = warning_messages[0] if warning_messages else None
    return coerce_resolved_block(block, resolved_values, resolution_status, message)


def _merge_resolution_status(current_status: str, next_status: str) -> str:
    if "error" in {current_status, next_status}:
        return "error"
    if "partial" in {current_status, next_status}:
        return "partial"
    return "ok"
