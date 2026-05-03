# Bay Street MCP

**A regulatory backstop for Canadian fintech architects: validate designs, vendor selections, and incident responses against OSFI, PIPEDA, FINTRAC, and Quebec Law 25 without leaving your editor.**

> Architecture review at design time. Regulatory text at query time. Built for senior architects working with LLMs at Canadian financial institutions.

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
| End-to-end smoke test against an MCP client (Claude Desktop, Cursor, Cline) | ⬜ Planned |
| PIPEDA full text | ⬜ Planned |
| FINTRAC AML/ATF guidance | ⬜ Planned |
| Quebec Law 25 | ⬜ Planned |
| Demo recording + first public release (v0.1.0 tag) | ⬜ Planned |

If you want this for your Canadian fintech AI tooling, watch or star the repo. Substantive feedback on the roadmap is welcome via Issues.

## Demo

*Demo lands with the v0.1.0 release: a 90-second screen recording showing an MCP client (Claude Desktop in the demo) calling `compliance_lookup` and answering a regulatory question with a citation back to the source document.*

## Why I built this

I have spent 20 years architecting platforms in Canadian financial services. The regulatory review of new designs has always been a slow, expensive, late-stage step. By the time legal or compliance surfaces an issue, the architecture is locked, the build is in progress, and the rework is painful.

Bay Street MCP puts the regulatory backstop where it belongs: at design time, in the architect's editor, alongside your LLM of choice. The server exposes Canadian financial regulation as queryable context. Your LLM reads your architecture, queries the relevant provisions, and surfaces the implications before they become rework.

## How architects use this

Bay Street MCP shines at the four moments where architects need regulatory context without leaving their editor:

1. **Pre-design check.** *"I'm building a real-time fraud detection system that uses customer transaction data. What regulatory considerations should shape the design?"* Your LLM queries Bay Street MCP and returns OSFI E-21 (operational risk) plus PIPEDA (data handling) considerations grounded in the source text.

2. **Architecture review augmentation.** Paste your design (Mermaid diagram, ADR, RFC, system diagram). Your LLM reads it, queries the relevant provisions, and surfaces a structured regulatory review: *"Your design includes [X]. OSFI [section Y] requires [Z]. Recommendation: [W]."*

3. **Vendor and third-party evaluation.** *"We're considering [SaaS vendor]. They process PII for our customers. What PIPEDA and Quebec Law 25 considerations apply to this contract?"* Get cited passages on consent, retention, cross-border transfer, and breach notification.

4. **Incident response.** *"We had a 6-hour outage of our funds-transfer service. What are our regulatory reporting obligations?"* Get the specific E-21 incident reporting requirements with citations.

The MCP server is the knowledge backstop. Your LLM is the reasoning engine. You stay the human-in-the-loop deciding what to ship.

## Quick start (planned for v0.1, not yet functional)

The instructions below describe how the server will work once v0.1.0 ships. They do not work against the current commit. Tracking progress is in the Status table above.

The example uses Claude Desktop because it is the most widely deployed MCP client. Bay Street MCP works with any MCP client (Cursor, Cline, Claude Code, Continue, Goose, etc.); the install step varies by client but the underlying server invocation is the same.

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

5. Restart Claude Desktop (or your MCP client of choice). Ask:

   > *What does OSFI E-21 say about AI risk management?*

   The LLM will call `compliance_lookup` and answer with citations.

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
- [ ] End-to-end demo against an MCP client (Loom)
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
User question  →  LLM  →  MCP tool call  →  Chroma similarity search
       →  top-k passages with metadata  →  LLM synthesizes answer with citations
```

The ingestion script chunks each regulation by ~800 words with 100-word overlap, stores in Chroma with metadata `{regulation, jurisdiction, page, source_url}`. The MCP tool returns passages with full citation metadata, so the LLM can cite page numbers and source URLs in its response.

## Why MCP

MCP (Model Context Protocol) is becoming the standard interface for connecting LLMs to external context. Exposing this as an MCP server means the same compliance knowledge is usable from any MCP-compatible client (Claude Desktop, Cursor, Cline, Claude Code, Continue, Goose, and others) and any underlying model the client supports, without building a custom integration each time.

Because MCP separates the knowledge layer from the model layer, the same Bay Street MCP install works with any model the client supports: Claude, Mistral, OpenAI (including their open-weight `gpt-oss` models), Llama, or any local model via Ollama or vLLM. Useful for on-prem deployments, data-residency-sensitive workflows where cloud LLMs are not allowed, and cost-sensitive batch use cases. The knowledge layer (Canadian regulatory text) and the reasoning layer (whichever LLM you choose) are deliberately decoupled.

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
