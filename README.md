# Bay Street MCP

**A Model Context Protocol server that lets Claude (and any MCP client) cite actual Canadian financial-services regulations: OSFI, PIPEDA, FINTRAC, Quebec Law 25.**

> Stop your AI from hallucinating compliance answers for Canadian fintech.

[![CI](https://github.com/ziamalik/bay-street-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/ziamalik/bay-street-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Status: Early Development](https://img.shields.io/badge/status-early%20development-orange)](https://github.com/ziamalik/bay-street-mcp)

## Status

🚧 **Early development.** Project scaffolding and v0.1 roadmap landed in the initial commit. First working release (v0.1.0) targeted for roughly 6 weeks out, built incrementally. Watch the commit history for weekly progress.

| Component | State |
|---|---|
| Project scaffolding, CI, license, dependencies, MCP server stub | ✅ Shipped |
| OSFI Guideline E-21 ingestion working | 🚧 Up next |
| `compliance_lookup` MCP tool returning real cited passages | ⬜ Planned |
| End-to-end Claude Desktop smoke test | ⬜ Planned |
| PIPEDA full text | ⬜ Planned |
| FINTRAC AML/ATF guidance | ⬜ Planned |
| Quebec Law 25 | ⬜ Planned |
| Demo recording + first public release (v0.1.0 tag) | ⬜ Planned |

If you want this for your Canadian fintech AI tooling, watch or star the repo. Substantive feedback on the roadmap is welcome via Issues.

## Demo

*Demo lands with the v0.1.0 release: a 90-second screen recording showing Claude Desktop calling `compliance_lookup` and answering a regulatory question with a citation back to the source document.*

## Why I built this

I have spent 20 years in Canadian financial services (TD, Canada Life, Gore Mutual). Every Canadian fintech I have spoken to that is shipping AI features hits the same wall: their LLM confidently makes up answers about OSFI E-21 risk management or PIPEDA disclosure obligations because the training data has 100x more US/EU regulation than Canadian.

This MCP server fixes that. Point Claude at it, ask any question about Canadian financial regulation, and get an answer grounded in the actual document with citations.

## Quick start (planned for v0.1, not yet functional)

The instructions below describe how the server will work once v0.1.0 ships. They do not work against the current commit. Tracking progress is in the Status table above.

1. Clone and install:

   ```bash
   git clone https://github.com/ziamalik/bay-street-mcp.git
   cd bay-street-mcp
   uv sync
   ```

2. Download a regulation PDF. For the v0.1 example, grab OSFI Guideline E-21 (Operational Risk Management and Resilience) from <https://www.osfi-bsif.gc.ca/>.

3. Ingest it:

   ```bash
   uv run bay-street-ingest data/osfi-e21.pdf \
     --regulation "OSFI Guideline E-21" \
     --jurisdiction CA \
     --source-url "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/operational-risk-management-resilience"
   ```

4. Add to your `claude_desktop_config.json` (typically at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

   ```json
   {
     "mcpServers": {
       "bay-street": {
         "command": "uv",
         "args": ["--directory", "/absolute/path/to/bay-street-mcp", "run", "bay-street-mcp"]
       }
     }
   }
   ```

   See `claude_desktop_config.example.json` for an alternative invocation if you have installed the package globally.

5. Restart Claude Desktop. Ask:

   > *What does OSFI E-21 say about AI risk management?*

   Claude will call `compliance_lookup` and answer with citations.

## What v0.1 will deliver (when shipped)

- One MCP tool: `compliance_lookup(query, top_k)` returning passages with `{regulation, jurisdiction, page, source_url}` citation metadata
- One regulation supported out of the box: OSFI Guideline E-21 (you load the PDF)
- Chroma vector store, persistent on disk
- Stdio transport (works with Claude Desktop, Claude Code, Cursor, any MCP client)
- About 400 lines of Python

Subsequent versions add PIPEDA, FINTRAC, Quebec Law 25, then expand to OSFI E-23 (model risk) and B-13 (technology and cyber risk). See Roadmap below.

## Roadmap

**v0.1 (in progress, ETA ~6 weeks):**
- [x] Project scaffolding, CI, license, dependencies, MCP server stub
- [ ] OSFI Guideline E-21 ingestion working end-to-end
- [ ] `compliance_lookup` MCP tool returning real cited passages
- [ ] End-to-end Claude Desktop demo (Loom)
- [ ] First public release (v0.1.0 tag)

**v0.2 and beyond:**
- [ ] PIPEDA full text + summary
- [ ] FINTRAC AML/ATF guidance
- [ ] Quebec Law 25
- [ ] OSFI E-23 (model risk management)
- [ ] OSFI B-13 (technology and cyber risk)
- [ ] Auto-refresh from regulator sites with diff detection
- [ ] Resource endpoints for whole-document retrieval
- [ ] Citation formatting (APA, plain-text)
- [ ] Pre-built Docker image

## How it works

```
User question  →  Claude  →  MCP tool call  →  Chroma similarity search
       →  top-k passages with metadata  →  Claude synthesizes answer with citations
```

The ingestion script chunks each regulation by ~800 words with 100-word overlap, stores in Chroma with metadata `{regulation, jurisdiction, page, source_url}`. The MCP tool returns passages with full citation metadata, so Claude can cite page numbers and source URLs in its response.

## Why MCP

MCP (Model Context Protocol) is becoming the standard interface for connecting LLMs to external context. Exposing this as an MCP server means the same compliance knowledge is usable from Claude Desktop, Claude Code, Cursor, and any future MCP client without building a custom integration each time.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
```

## License

MIT. Use it, fork it, ship it.

## About

Built by Zia Malik — 20 years Canadian financial services, currently building [AppVet](https://appvet.dev) (AI-powered web app security audits) and writing about fintech-grade AI engineering.

If you are at a Canadian fintech and want this extended for your specific regulatory surface, open an issue or reach out.
