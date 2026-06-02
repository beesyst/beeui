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


# Чтение top-level blocks и валидация каждого описания через renderer contract
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


# Чтение pages[].blocks[] и чек ссылки на уже объявленные block ids
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

        unknown_keys = sorted(set(item) - {"block", "width"})
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

        width = item.get("width")
        if not isinstance(width, int) or width < 1 or width > 12:
            raise ValueError(
                f"pages[{page_index}].blocks[{block_index}].width must be an integer in range 1..12"
            )

        placements.append(BlockPlacement(block_id=block_id, width=width))

    return placements


# Коннект placement и definition в модель, которую можно передать в template
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
                placement.width,
            )
        )
    return rendered


# Принятие разрешенного блока и данных из резолвера, их объединение и повторная валидация для рендера, с учётом возможных ошибок разрешения данных
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


# Объединение статусов разрешения данных, где "error" > "partial" > "ok"
def _merge_resolution_status(current_status: str, next_status: str) -> str:
    if "error" in {current_status, next_status}:
        return "error"
    if "partial" in {current_status, next_status}:
        return "partial"
    return "ok"
