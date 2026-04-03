from app import db
from app.models.block import Block


class BlockService:

    @staticmethod
    def create_block(page_id: int, data: dict) -> Block:
        """Create a block on a page."""
        block = Block(
            page_id=page_id,
            type=data["type"],
            order=data.get("order", 0),
            props=data.get("props", {}),
        )
        db.session.add(block)
        db.session.commit()
        return block

    @staticmethod
    def get_blocks_by_page(page_id: int) -> list[Block]:
        """Return all blocks for a page, ordered."""
        return (
            Block.query
            .filter_by(page_id=page_id)
            .order_by(Block.order.asc())
            .all()
        )

    @staticmethod
    def get_block_by_id(block_id: int) -> Block | None:
        """Return a single block by ID."""
        return Block.query.get(block_id)

    @staticmethod
    def update_block(block: Block, data: dict) -> Block:
        """Update a block's props and/or order. Props are merged (patch-style)."""
        if "props" in data:
            # Merge props: existing + incoming (allows partial prop updates)
            merged = {**(block.props or {}), **data["props"]}
            block.props = merged

        if "order" in data:
            block.order = data["order"]

        if "type" in data:
            block.type = data["type"]

        db.session.commit()
        return block

    @staticmethod
    def delete_block(block: Block) -> None:
        """Delete a single block."""
        db.session.delete(block)
        db.session.commit()

    @staticmethod
    def reorder_blocks(page_id: int, ordered_ids: list[int]) -> list[Block]:
        """
        Reorder blocks for a page.
        ordered_ids: list of block IDs in desired order, e.g. [3, 1, 2]
        """
        blocks = Block.query.filter(
            Block.id.in_(ordered_ids),
            Block.page_id == page_id,
        ).all()

        # Validate all IDs belong to the page
        if len(blocks) != len(ordered_ids):
            raise ValueError("Some block IDs are invalid or don't belong to this page.")

        block_map = {b.id: b for b in blocks}
        for new_order, block_id in enumerate(ordered_ids):
            block_map[block_id].order = new_order

        db.session.commit()
        return sorted(blocks, key=lambda b: b.order)
