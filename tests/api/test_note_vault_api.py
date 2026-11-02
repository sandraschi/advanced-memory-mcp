"""Backend contracts the Note Vault webapp depends on: global sort, backlinks, body editing."""

from urllib.parse import quote

import pytest
import pytest_asyncio
from httpx import AsyncClient

from advanced_memory.schemas.search import SearchResponse

TITLES = ["Echo Note", "alpha note", "Delta Note", "charlie note", "Bravo Note"]


async def _create(client: AsyncClient, project_url: str, title: str, content: str = "body", folder: str = "vault"):
    response = await client.post(
        f"{project_url}/knowledge/entities",
        json={"title": title, "folder": folder, "entity_type": "note", "content": content},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def _search(client: AsyncClient, project_url: str, sort: str | None, page: int, page_size: int):
    body: dict = {"entity_types": ["entity"]}
    if sort is not None:
        body["sort"] = sort
    response = await client.post(f"{project_url}/search/?page={page}&page_size={page_size}", json=body)
    assert response.status_code == 200, response.text
    return SearchResponse.model_validate(response.json())


async def _all_pages(client: AsyncClient, project_url: str, sort: str, page_size: int = 2) -> list[str]:
    """Walk every page and return titles in the order the server produced them."""
    titles: list[str] = []
    page = 1
    while True:
        result = await _search(client, project_url, sort, page, page_size)
        titles.extend(r.title for r in result.results)
        if page * page_size >= result.total_results:
            return titles
        page += 1


@pytest_asyncio.fixture
async def vault_notes(client: AsyncClient, project_url: str, init_search_index):
    """Five notes created in a known order so created_* sorts are predictable."""
    for title in TITLES:
        await _create(client, project_url, title)
    return TITLES


@pytest.mark.asyncio
async def test_sort_title_is_global_across_pages(client, project_url, vault_notes):
    asc = await _all_pages(client, project_url, "title_asc")
    assert asc == sorted(vault_notes, key=str.lower)

    desc = await _all_pages(client, project_url, "title_desc")
    assert desc == sorted(vault_notes, key=str.lower, reverse=True)


@pytest.mark.asyncio
async def test_sort_created_oldest_first_means_oldest_of_all(client, project_url, vault_notes):
    """Page 1 of created_asc must hold the very first note created, not just the oldest of some page."""
    first_page = await _search(client, project_url, "created_asc", 1, 2)
    assert first_page.results[0].title == vault_notes[0]

    asc = await _all_pages(client, project_url, "created_asc")
    assert asc == vault_notes
    desc = await _all_pages(client, project_url, "created_desc")
    assert desc == list(reversed(vault_notes))


@pytest.mark.asyncio
async def test_sort_modified_matches_edit_order(client, project_url, vault_notes):
    """Editing the oldest note moves it to the top of modified_desc and the bottom of modified_asc."""
    edited = vault_notes[0]
    response = await client.patch(
        f"{project_url}/knowledge/entities/{quote('vault/echo-note', safe='/')}",
        json={"operation": "replace_body", "content": "edited later"},
    )
    assert response.status_code == 200, response.text

    desc = await _all_pages(client, project_url, "modified_desc")
    asc = await _all_pages(client, project_url, "modified_asc")
    assert desc[0] == edited
    assert asc[-1] == edited


@pytest.mark.asyncio
async def test_sort_keeps_total_and_default_still_works(client, project_url, vault_notes):
    sorted_page = await _search(client, project_url, "title_asc", 1, 2)
    default_page = await _search(client, project_url, None, 1, 2)
    relevance_page = await _search(client, project_url, "relevance", 1, 2)
    assert sorted_page.total_results == default_page.total_results == relevance_page.total_results


@pytest.mark.asyncio
async def test_sort_rejects_unknown_value(client, project_url, vault_notes):
    response = await client.post(
        f"{project_url}/search/", json={"entity_types": ["entity"], "sort": "title; DROP TABLE entity"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_backlinks_lists_notes_that_link_here(client, project_url, init_search_index):
    await _create(client, project_url, "Target Note", content="the target")
    await _create(
        client, project_url, "Source One", content="# Source One\n\n## Relations\n- links_to [[Target Note]]\n"
    )
    await _create(
        client, project_url, "Source Two", content="# Source Two\n\n## Relations\n- depends_on [[Target Note]]\n"
    )
    await _create(client, project_url, "Unrelated", content="nothing to see")

    response = await client.get(f"{project_url}/knowledge/backlinks/vault/target-note")
    assert response.status_code == 200, response.text
    data = response.json()
    by_title = {b["title"]: b for b in data["backlinks"]}
    assert set(by_title) == {"Source One", "Source Two"}
    assert by_title["Source One"]["relation_type"] == "links_to"
    assert by_title["Source Two"]["relation_type"] == "depends_on"
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_backlinks_includes_unresolved_forward_reference(client, project_url, init_search_index):
    """A note that links to [[Later Note]] before it exists is a backlink once it does."""
    await _create(
        client, project_url, "Early Bird", content="# Early Bird\n\n## Relations\n- mentions [[Later Note]]\n"
    )
    await _create(client, project_url, "Later Note", content="arrived afterwards")

    response = await client.get(f"{project_url}/knowledge/backlinks/vault/later-note")
    assert response.status_code == 200, response.text
    assert [b["title"] for b in response.json()["backlinks"]] == ["Early Bird"]


@pytest.mark.asyncio
async def test_backlinks_excludes_self_and_404s_unknown(client, project_url, init_search_index):
    await _create(client, project_url, "Narcissus", content="# Narcissus\n\n## Relations\n- admires [[Narcissus]]\n")
    response = await client.get(f"{project_url}/knowledge/backlinks/vault/narcissus")
    assert response.status_code == 200
    assert response.json()["backlinks"] == []

    missing = await client.get(f"{project_url}/knowledge/backlinks/vault/does-not-exist")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_editor_roundtrip_replace_body_preserves_identity(client, project_url, init_search_index):
    """The editor loads GET /content and saves PATCH replace_body; identity and text must survive."""
    created = await _create(client, project_url, "Editable", content="# Editable\n\nfirst draft\n")
    permalink = created["permalink"]
    content_url = f"{project_url}/knowledge/entities/{permalink}/content"

    loaded = (await client.get(content_url)).json()["content"]
    assert "first draft" in loaded

    new_body = loaded.replace("first draft", "second draft with [[Some Link]]")
    patched = await client.patch(
        f"{project_url}/knowledge/entities/{permalink}",
        json={"operation": "replace_body", "content": new_body},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["permalink"] == permalink

    reloaded = (await client.get(content_url)).json()["content"]
    assert "second draft with [[Some Link]]" in reloaded
    assert "first draft" not in reloaded


@pytest.mark.asyncio
async def test_date_range_filters_apply_to_whole_set(client, project_url, vault_notes):
    async def total(**extra) -> int:
        body = {"entity_types": ["entity"], "sort": "created_asc", **extra}
        response = await client.post(f"{project_url}/search/?page=1&page_size=2", json=body)
        assert response.status_code == 200, response.text
        return SearchResponse.model_validate(response.json()).total_results

    everything = await total()
    assert everything == len(vault_notes)

    assert await total(created_from="2000-01-01") == everything
    assert await total(created_to="2000-01-01") == 0
    assert await total(created_from="2999-01-01") == 0
    assert await total(modified_from="2000-01-01", modified_to="2999-01-01") == everything
    assert await total(modified_to="2000-01-01") == 0


@pytest.mark.asyncio
async def test_date_filter_alone_counts_as_a_criterion(client, project_url, vault_notes):
    """A bare date bound must not hit the 'no criteria -> empty' short circuit."""
    response = await client.post(f"{project_url}/search/", json={"created_from": "2000-01-01"})
    assert response.status_code == 200
    assert SearchResponse.model_validate(response.json()).total_results >= len(vault_notes)
