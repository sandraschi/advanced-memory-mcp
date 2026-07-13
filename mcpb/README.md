# advanced-memory-mcp (MCPB Bundle)

Comprehensive research and knowledge platform with web search, GitHub trawling, arXiv academic research, TV Tropes narrative analysis, document ingestion, RAG vector search, and research-driven skill creation

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "advanced_memory_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **main_stdio**: main(stdio)
- **main_http**: main(http)
- **main_sse**: main(sse)
- **health_check**: health_check
- **optimize_model_params**: optimize_model_params
- **import_batch**: import_batch
- **move_entity**: move_entity
- **knowledge_graph_subgraph**: knowledge_graph_subgraph
- **get_file_sync_status**: get_file_sync_status
- **get_rag_extra_roots**: get_rag_extra_roots
- **put_rag_extra_roots**: put_rag_extra_roots
- **validate_rag_extra_roots**: validate_rag_extra_roots
- **sync_project**: sync_project
- **get_resource_content**: get_resource_content
- **write_resource**: write_resource
- **reindex**: Recreate and populate the search index.
- **list_recent_logs**: list_recent_logs
- **greet_dev**: greet(dev)
- **greet_prod**: greet(prod)
- **greet_test**: greet(test)
- **adn_arxiv_research_relevance**: adn_arxiv_research(relevance)
- **adn_arxiv_research_lastUpdatedDate**: adn_arxiv_research(lastUpdatedDate)
- **adn_arxiv_research_submittedDate**: adn_arxiv_research(submittedDate)
- **adn_github_research_stars**: adn_github_research(stars)
- **adn_github_research_forks**: adn_github_research(forks)
- **adn_github_research_updated**: adn_github_research(updated)
- **adn_github_research_best_match**: adn_github_research(best-match)
- **adn_tvtropes_research_all**: adn_tvtropes_research(all)
- **adn_tvtropes_research_film**: adn_tvtropes_research(film)
- **adn_tvtropes_research_literature**: adn_tvtropes_research(literature)
- **adn_tvtropes_research_tv**: adn_tvtropes_research(tv)
- **adn_tvtropes_research_video_games**: adn_tvtropes_research(video_games)
- **adn_tvtropes_research_webcomics**: adn_tvtropes_research(webcomics)
- **adn_tvtropes_research_music**: adn_tvtropes_research(music)
- **adn_visualize_point_cloud**: adn_visualize(point_cloud)
- **adn_visualize_hub_and_spoke**: adn_visualize(hub_and_spoke)
- **adn_visualize_temporal**: adn_visualize(temporal)
- **adn_web_search_duckduckgo**: adn_web_search(duckduckgo)
- **adn_web_search_serpapi**: adn_web_search(serpapi)
- **adn_web_search_bing**: adn_web_search(bing)
- **adn_web_search_auto**: adn_web_search(auto)
- **adn_audio**: adn_audio
- **adn_automation**: adn_automation
- **adn_inbox**: adn_inbox
- **adn_knowledge_rag**: adn_knowledge_rag
- **adn_knowledge**: adn_knowledge
- **adn_nav**: adn_nav
- **adn_notes**: adn_notes
- **adn_project**: adn_project
- **adn_rag_fixed**: adn_rag(fixed)
- **adn_rag_semantic**: adn_rag(semantic)
- **adn_rag_sentence**: adn_rag(sentence)
- **adn_search**: adn_search
- **_load_metadata_scaffold**: _load_metadata(scaffold)
- **_load_metadata_validate**: _load_metadata(validate)
- **_load_metadata_package**: _load_metadata(package)
- **_load_metadata_inspect**: _load_metadata(inspect)
- **_load_metadata_upgrade**: _load_metadata(upgrade)
- **_load_skill_content_structured**: _load_skill_content(structured)
- **_load_skill_content_raw**: _load_skill_content(raw)
- **_load_skill_content_metadata_only**: _load_skill_content(metadata_only)
- **adn_skills_research_bundle**: adn_skills_research(bundle)
- **adn_skills_research_skill_draft**: adn_skills_research(skill_draft)
- **adn_skills**: adn_skills
- **adn_system**: adn_system
- **adn_typora**: adn_typora
- **adn_zettel**: adn_zettel
- **dictate**: dictate
- **speak**: speak
- **listen**: listen
- **wake_start**: wake_start
- **wake_stop**: wake_stop
- **wake_status**: wake_status
- **weather**: weather
- **timer**: timer
- **alarm**: alarm
- **music**: music
- **build_success_response_add**: build_success_response(add)
- **build_success_response_remove**: build_success_response(remove)
- **build_success_response_replace**: build_success_response(replace)
- **build_success_response_clear**: build_success_response(clear)
- **tool_function**: tool_function
- **status**: status
- **process**: process
- **info**: info
- **watch**: watch
- **adn_knowledge_bulk**: adn_knowledge_bulk
- **summarize**: summarize
- **enhance**: enhance
- **suggest_tags**: suggest_tags
- **qc**: qc
- **summarize_find_runts**: summarize(find_runts)
- **summarize_find_junk**: summarize(find_junk)
- **ingest**: ingest
- **export**: export
- **canvas**: canvas
- **load**: load
- **ingest_obsidian**: ingest(obsidian)
- **ingest_notion**: ingest(notion)
- **ingest_joplin**: ingest(joplin)
- **ingest_evernote**: ingest(evernote)
- **ingest_onenote**: ingest(onenote)
- **ingest_archive**: ingest(archive)
- **build_context**: build_context
- **recent**: recent
- **ls**: ls
- **backlinks**: backlinks
- **sync**: sync
- **write**: write
- **read**: read
- **edit**: edit
- **delete**: delete
- **move**: move
- **quick**: quick
- **daily**: daily
- **write_append**: write(append)
- **write_prepend**: write(prepend)
- **write_replace_section**: write(replace_section)
- **write_find_replace**: write(find_replace)
- **adn_import_export_import**: adn_import_export(import)
- **adn_import_export_export**: adn_import_export(export)
- **adn_import_export_load**: adn_import_export(load)
- **adn_import_export_search**: adn_import_export(search)
- **list_memory_projects**: list_memory_projects
- **create_memory_project**: create_memory_project
- **create**: create
- **switch**: switch
- **rm**: rm
- **detect**: detect
- **query**: query
- **rag**: rag
- **external**: external
- **query_text**: query(text)
- **query_title**: query(title)
- **query_permalink**: query(permalink)
- **query_tag**: query(tag)
- **list_skills**: list_skills
- **update**: update
- **activate**: activate
- **deactivate**: deactivate
- **active**: active
- **load_section**: load_section
- **load_resource**: load_resource
- **research**: research
- **create_beginner**: create(beginner)
- **create_intermediate**: create(intermediate)
- **create_advanced**: create(advanced)
- **create_expert**: create(expert)
- **workflow**: workflow
- **help**: help
- **status_basic**: status(basic)
- **status_detailed**: status(detailed)
- **status_expert**: status(expert)
- **open**: open
- **save**: save
- **get_content**: get_content
- **set_content**: set_content
- **insert**: insert
- **cursor**: cursor
- **analyze**: analyze
- **open_pdf**: open(pdf)
- **open_html**: open(html)
- **open_docx**: open(docx)
- **open_odt**: open(odt)
- **generate**: generate
- **suggest**: suggest
- **expand**: expand
- **connect**: connect
- **collect**: collect
- **customize**: customize
- **generate_quick**: generate(quick)
- **generate_standard**: generate(standard)
- **generate_comprehensive**: generate(comprehensive)
- **generate_expert**: generate(expert)
- **adn_zettelmaker_generate**: adn_zettelmaker(generate)
- **adn_zettelmaker_customize**: adn_zettelmaker(customize)
- **adn_zettelmaker_expand**: adn_zettelmaker(expand)
- **adn_zettelmaker_suggest**: adn_zettelmaker(suggest)
- **adn_zettelmaker_connect**: adn_zettelmaker(connect)
- **adn_zettelmaker_analyze**: adn_zettelmaker(analyze)
- **adn_zettelmaker_collect**: adn_zettelmaker(collect)
- **portmanteau_fixed**: portmanteau(fixed)
- **portmanteau_semantic**: portmanteau(semantic)
- **portmanteau_sentence**: portmanteau(sentence)
- **portmanteau_docx**: portmanteau(docx)
- **portmanteau_html**: portmanteau(html)
- **portmanteau_pdf**: portmanteau(pdf)
- **portmanteau_txt**: portmanteau(txt)
- **generate_mermaid_diagram_flowchart**: generate_mermaid_diagram(flowchart)
- **generate_mermaid_diagram_sequence**: generate_mermaid_diagram(sequence)
- **generate_mermaid_diagram_gantt**: generate_mermaid_diagram(gantt)
- **generate_mermaid_diagram_mindmap**: generate_mermaid_diagram(mindmap)
- **generate_mermaid_diagram_er**: generate_mermaid_diagram(er)

## Requirements

- Python 3.12+
- uv
