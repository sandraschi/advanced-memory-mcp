"""Bounded link-neighborhood graph for the webapp (Obsidian-style local graph)."""

from __future__ import annotations

from typing import Any

from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import aliased

from advanced_memory import db
from advanced_memory.models.knowledge import Entity, Relation
from advanced_memory.repository.entity_repository import EntityRepository


def _entity_node_id(entity: Entity) -> str:
    if entity.permalink:
        return entity.permalink
    return f"entity:{entity.id}"


async def _relations_touching(
    session: AsyncSession,
    project_id: int,
    entity_ids: set[int],
    *,
    include_unresolved: bool,
) -> list[tuple[Relation, Entity, Entity | None]]:
    if not entity_ids:
        return []
    e_from = aliased(Entity)
    e_to = aliased(Entity)
    touch = or_(Relation.from_id.in_(entity_ids), Relation.to_id.in_(entity_ids))
    stmt = (
        select(Relation, e_from, e_to)
        .join(e_from, Relation.from_id == e_from.id)
        .outerjoin(e_to, Relation.to_id == e_to.id)
        .where(e_from.project_id == project_id)
        .where(touch)
    )
    if not include_unresolved:
        stmt = stmt.where(Relation.to_id.isnot(None))
    stmt = stmt.where(or_(Relation.to_id.is_(None), e_to.project_id == project_id))
    result = await session.execute(stmt)
    return list(result.all())


async def _load_entities(
    session: AsyncSession,
    project_id: int,
    ids: set[int],
    entity_by_id: dict[int, Entity],
    max_nodes: int,
) -> None:
    need = [i for i in ids if i not in entity_by_id]
    if not need:
        return
    cap = max(0, max_nodes - len(entity_by_id))
    if cap <= 0:
        return
    need = need[:cap]
    q = select(Entity).where(Entity.project_id == project_id, Entity.id.in_(need))
    r = await session.execute(q)
    for ent in r.scalars():
        entity_by_id[ent.id] = ent


async def fetch_link_subgraph(
    session_maker: async_sessionmaker[AsyncSession],
    project_id: int,
    entity_repository: EntityRepository,
    *,
    center: str | None,
    depth: int,
    max_nodes: int,
    max_edges: int,
    include_unresolved: bool,
    seed_size: int = 48,
) -> dict[str, Any]:
    """Return ``{ nodes, links, meta }`` for force-graph style UIs.

    With ``center`` (permalink or ``entity:<id>``): ego-graph by BFS up to ``depth``.
    Without ``center``: multi-source BFS from recently updated markdown notes.
    """
    depth = max(1, min(depth, 5))
    max_nodes = max(10, min(max_nodes, 5000))
    max_edges = max(10, min(max_edges, 20000))

    async with db.scoped_session(session_maker) as session:
        start_ids: list[int] = []

        if center and center.strip():
            c = center.strip()
            if c.startswith("entity:") and c[7:].isdigit():
                eid = int(c[7:])
                row = await session.execute(select(Entity).where(Entity.id == eid, Entity.project_id == project_id))
                ent = row.scalars().one_or_none()
                if ent is None:
                    return {
                        "nodes": [],
                        "links": [],
                        "meta": {"error": "center_not_found", "center": c},
                    }
                start_ids = [ent.id]
            else:
                ent = await entity_repository.get_by_permalink(c)
                if ent is None:
                    return {
                        "nodes": [],
                        "links": [],
                        "meta": {"error": "center_not_found", "center": c},
                    }
                start_ids = [ent.id]
        else:
            q = (
                select(Entity.id)
                .where(
                    Entity.project_id == project_id,
                    Entity.content_type == "text/markdown",
                )
                .order_by(Entity.updated_at.desc())
                .limit(seed_size)
            )
            res = await session.execute(q)
            start_ids = [r[0] for r in res.all()]
            if not start_ids:
                return {"nodes": [], "links": [], "meta": {"empty_project": True}}

        entity_by_id: dict[int, Entity] = {}
        links_out: list[dict[str, Any]] = []
        link_keys: set[tuple[str, str]] = set()
        ghost_labels: dict[str, str] = {}

        await _load_entities(session, project_id, set(start_ids), entity_by_id, max_nodes)
        if not entity_by_id:
            return {"nodes": [], "links": [], "meta": {"empty_project": True}}

        dist: dict[int, int] = {s: 0 for s in start_ids}
        frontier: set[int] = set(start_ids)

        for current_d in range(depth):
            if not frontier or len(links_out) >= max_edges:
                break
            rows = await _relations_touching(session, project_id, frontier, include_unresolved=include_unresolved)
            next_frontier: set[int] = set()

            for rel, ef, et in rows:
                if len(links_out) >= max_edges:
                    break

                expands = False
                if rel.from_id in frontier and dist.get(rel.from_id, -1) == current_d:
                    expands = True
                if rel.to_id and rel.to_id in frontier and dist.get(rel.to_id, -1) == current_d:
                    expands = True
                if not expands:
                    continue

                await _load_entities(session, project_id, {ef.id}, entity_by_id, max_nodes)
                if et is not None:
                    await _load_entities(session, project_id, {et.id}, entity_by_id, max_nodes)

                if et is not None:
                    if ef.id not in entity_by_id or et.id not in entity_by_id:
                        continue
                    sid = _entity_node_id(entity_by_id[ef.id])
                    tid = _entity_node_id(entity_by_id[et.id])
                    k = (sid, tid) if sid <= tid else (tid, sid)
                    if k not in link_keys:
                        link_keys.add(k)
                        links_out.append(
                            {
                                "source": sid,
                                "target": tid,
                                "relation_type": rel.relation_type,
                            }
                        )

                    if rel.from_id in frontier and dist.get(rel.from_id, -1) == current_d:
                        if rel.to_id and current_d + 1 < depth:
                            if dist.get(rel.to_id, 999) > current_d + 1:
                                dist[rel.to_id] = current_d + 1
                            next_frontier.add(rel.to_id)
                    if rel.to_id and rel.to_id in frontier and dist.get(rel.to_id, -1) == current_d:
                        if current_d + 1 < depth:
                            if dist.get(rel.from_id, 999) > current_d + 1:
                                dist[rel.from_id] = current_d + 1
                            next_frontier.add(rel.from_id)
                elif include_unresolved:
                    if ef.id not in entity_by_id:
                        continue
                    ghost_id = f"unresolved:{rel.id}"
                    ghost_labels[ghost_id] = rel.to_name
                    sid = _entity_node_id(entity_by_id[ef.id])
                    k = (sid, ghost_id)
                    if k not in link_keys:
                        link_keys.add(k)
                        links_out.append(
                            {
                                "source": sid,
                                "target": ghost_id,
                                "relation_type": rel.relation_type,
                            }
                        )

            frontier = {i for i in next_frontier if i in entity_by_id and dist.get(i, -1) == current_d + 1}

        nodes_out: list[dict[str, Any]] = []
        for ent in entity_by_id.values():
            nodes_out.append(
                {
                    "id": _entity_node_id(ent),
                    "label": ent.title or ent.file_path,
                    "type": "entity",
                    "entity_type": ent.entity_type,
                }
            )
        for gid, label in ghost_labels.items():
            nodes_out.append({"id": gid, "label": label, "type": "unresolved"})

        meta = {
            "node_count": len(nodes_out),
            "edge_count": len(links_out),
            "depth": depth,
            "max_nodes": max_nodes,
            "max_edges": max_edges,
            "center": center,
        }
        logger.debug("graph subgraph {}", meta)
        return {"nodes": nodes_out, "links": links_out, "meta": meta}
