# Plan: from local MCP server to a hosted one on Cloudflare

Status: draft, 2026-11-25. Not approved. Hosting is Ramsey's "access over the internet" decision (`.claude/docs/client-setup.md`); it is recorded in `unfccc/docs/decisions.md` before step 4.

## Where we are

- The server (`mcp_server/src/research_mcp/`) has seven read-only tools and runs only over stdio (`server.py`, `main()`), started by Claude Desktop on the same machine.
- The workspace root comes from `TI_RESEARCH_ROOT`, otherwise from the folder holding the code (`workspace.py`).
- Search needs `literature/unfccc/data/processed/index/` (26 MB) and `literature/unfccc/data/processed/text/` (17 MB). Both were committed locally on 2026-11-25 (commit "add knowledge base", not yet pushed), together with the downloaded PDFs and saved pages in `literature/unfccc/data/raw/`. If that commit is pushed, the image can be built from git alone and step 3 (R2) is not needed; if the PDFs, pages and text are taken out of git for licence reasons (see "Before anything is built", item 2), step 3 stays.
- The embedding model is fastembed (ONNX) with numpy and pandas. That rules out a plain Cloudflare Worker, including Python Workers, so the server runs in a Cloudflare Container.
- The repo `ramseywise/transparency-international` is public, and `main` is pushed up to the commit before "add knowledge base".

## Target

```
claude.ai / Desktop ──HTTPS──▶ Worker (sign-in, routing)  ──▶ Container (research_mcp, HTTP mode)
                                   │                               │
                         allowed GitHub accounts          repo copy + R2 bucket (index, text)
```

- One Worker in the same Cloudflare account as kiez, on its own hostname: a neutral domain (preferred), `research.waslosheute.app`, or `*.workers.dev`.
- Researchers add the address in claude.ai under Settings → Connectors → "Add custom connector" and sign in with GitHub.
- The tools stay read-only, and `data/` is still never served.

## Before anything is built

1. **`.claude/docs/` must be in git.** The hosted copy is built from git, and `get_operating_guide` serves the governance, evidence and workflow documents from this folder. The ignore line has been removed; the folder must be committed before the first build.
2. **The repo stays public** (Ramsey, 2026-11-25: "all of this data is public"; row in `unfccc/docs/decisions.md`). Two points are left open by that decision: (a) whether the downloaded copies of copyrighted sources (PDFs, saved pages, extracted text) may be redistributed from a public repo, which is a licence question, not a question of whether the source is publicly readable (S18); (b) naming an organisation as fossil-linked in a report is still a publication-sensitive decision for the lead researcher (rule 7). A draft classification in the repo is not a report, but anyone can read it.
3. **A personal-data check before writing.** Add one rule to `CLAUDE.md` (and the `/check-work` reviewers): before writing or committing anything, check it for personal data (names of individuals, contact details, anything beyond an organisation). If any is found, stop and ask the researcher how to handle it, with options. This extends rule 8. It changes `CLAUDE.md`, so `/run-evals` follows.

## Steps

### 1. HTTP mode next to stdio (code, local)

- `main()` takes `--http` (or `TI_MCP_TRANSPORT=http`) and then runs stateless Streamable HTTP (`stateless_http=True`, `host="0.0.0.0"`, `port=8080`). Without the flag it stays on stdio, so the Desktop config does not change.
- Add a `/health` route that reports the git commit served, the index date from the R2 manifest, and whether the index loaded.
- Load the embedding model once, at start-up rather than on the first query, and point fastembed's cache at a folder inside the image.
- **Errors.** `NotAvailable` already reaches the client as a tool error with its message, so rule 4 holds. Add one wrapper for everything else: bad arguments say what is wrong; any other exception gives a generic "could not complete this call", so paths and stack traces never leak.
- **Teaching the client.** The instructions sent on connect are not shown by every client. Offer the same text as an MCP prompt as well as the `research://guide` resource. Each tool description names the neighbouring tool to use instead (for example, `search_research` for decisions, `search_literature` for sources).
- **Measure the cost.** Record the token count of `tools/list` plus the instructions in `client-setup.md`, so growth shows.
- Tests in `mcp_server/tests/`:
  - the exact list of tool names, so that a tool added or removed is noticed;
  - a table of example inputs that covers every tool, and fails if a tool has no row or a row names no tool;
  - the same checks with the SDK client against the running HTTP server, not only the in-process call;
  - a write is impossible, and `data/` is refused;
  - without the index, search returns a tool error, not an empty result (rule 4: an unavailable tool is not evidence that a source does not exist).
- **Tool-choice eval.** Run the demo questions from `client-setup.md` on Haiku, Sonnet and Opus and score whether the right tool is called first. Run it before and after any change to descriptions. It costs model calls, so it is run by hand, not on every push.

### 2. The container image (local)

`mcp_server/Dockerfile`:

- Python slim with a pinned `uv` version, `uv sync --frozen --no-dev`, in two stages so build tools are not in the final image.
- Runs as a non-root user. A `HEALTHCHECK` on `/health` with a start period long enough for the model to load.
- `.dockerignore` excludes `.git`, `.env*`, tests, every `data/` folder, and the PDFs and saved pages.
- The embedding model is downloaded at build time, so there is no network fetch at start-up.
- The repo is copied in at build time, giving one image per commit, so a running server always matches one commit.
- At start, `literature/unfccc/data/processed/index/` and `literature/unfccc/data/processed/text/` are pulled from R2, then the server starts with `TI_RESEARCH_ROOT=/app`.
- Test locally with `docker run -p 8080:8080` and MCP Inspector (`npx @modelcontextprotocol/inspector`) against `http://localhost:8080/mcp`.

### 3. Private storage (Cloudflare, by Ramsey)

- Create an R2 bucket, for example `ti-research-library`. It is private, with no public URL.
- `literature/sync_r2.py` uploads `index/` and `text/` after each `rag index`, and writes a small manifest (file hashes, date) so the container can say which index it serves.
- The PDFs and saved pages are not uploaded. The server never serves them.

### 4. The Worker with sign-in

`mcp_server/cloudflare/` with `wrangler.jsonc`, following Cloudflare's remote-MCP template with GitHub OAuth (`workers-oauth-provider`):

- **GitHub OAuth app.** Callback `https://<host>/callback`. The client ID and secret are Worker secrets set with `wrangler secret put` and never committed.
- **Discovery.** Clients such as claude.ai find the sign-in by themselves: an unsigned request to `/mcp` gets `401` with `WWW-Authenticate: Bearer resource_metadata=…`, and `/.well-known/oauth-protected-resource` and `/.well-known/oauth-authorization-server` describe the rest. Check that `workers-oauth-provider` serves all three, and test them before the first sign-in.
- **Allowed accounts.** A list of allowed GitHub usernames as a Worker variable, checked on every request, not only at sign-in, so removing someone takes effect at once.
- **Tokens.** Issued for this server's `/mcp` address only, with one read-only scope. There are no write scopes because there are no write tools.
- **Limits.** A rate limit on sign-in and on `/mcp` per address. A kill switch: one Worker variable that refuses every call without a redeploy.
- **Not Cloudflare Access.** Access in front of `/mcp` would block MCP clients, which cannot pass its login page. Sign-in stays in the Worker.
- **Container binding.** `/mcp` is forwarded to the container only after sign-in. One instance is enough for a few researchers, and it sleeps when idle.
- **Route.** `{ "pattern": "<host>", "custom_domain": true }`, as kiez does it.
- **Logs.** Only the tool name, the GitHub user, the client name and the time are recorded, never query text. Queries can contain research questions about named organisations.

### 5. Deploy and check (Ramsey runs; the assistant prepares)

1. Record the decision row: host, who may sign in, what is served, what is not.
2. Upload the library to R2 with the sync script, then run `wrangler deploy` from `mcp_server/cloudflare/`.
3. Check the deployment:
   - `/health` shows the expected commit and index;
   - an account not on the list is refused;
   - an allowed account sees seven tools;
   - `search_literature` returns results with source IDs;
   - asking for anything in `data/` is refused.
4. Add the connector in claude.ai for one researcher. Run the demo questions from `client-setup.md` and compare the answers with the local server's.
5. Write a short "What was checked / Not checked" list at the end of `client-setup.md`: which clients were tried, and what was not tested (for example, a token revoked mid-session).

### 6. Keeping it current

- A GitHub Action runs the offline tests (`uv run pytest -q`) on every push and pull request, with no secrets. A second Action, on push to `main` only, builds the image and deploys; only it holds the Cloudflare API token. Until then, `wrangler deploy` by hand.
- `client-setup.md` gets a troubleshooting section (sign-in loops, cold start, "index unavailable"), and the repo gets a committed `.mcp.json` using `${CLAUDE_PROJECT_DIR}`, so a fresh clone connects without editing paths.
- After each `rag index` run the sync script. The manifest shows the date of the index the server serves.

## Changing studies through pull requests

This is separate from the server. Researchers who want to start or change a study use Claude Code on the web (claude.ai/code), connected to the repo:

- It loads `CLAUDE.md`, the skills, the agents and the hooks, works on a branch, and opens a pull request.
- Protect `main` so that merging needs Ramsey's review, and add each researcher as a collaborator.
- Before others create studies, generalise `.gitignore` to `*/data/raw/` and `*/data/processed/delegates_*`.
- Cloud sessions get only what is in git. The literature stages need a setup step that pulls the library from R2.

## Costs and limits

- **Cost.** Workers Paid ($5 a month, which may already cover kiez); container time while awake; R2 storage under 100 MB (cents); a neutral domain about €10 a year.
- **Cold start.** The first query after the container has been idle waits for it to wake and load the model, roughly 10 to 30 seconds (to be measured in step 2).
- **What it does not do.** Run skills, run Python for the researcher, or write files. Those still need Claude Code.
- **Left out on purpose.** Personal access tokens, dynamic client registration, per-tool scopes and usage dashboards (all in Spell's server) are for many users and write tools. With a few researchers and read-only tools, GitHub sign-in plus an allowed list is enough. Revisit if write tools are approved.

## Where the additions come from

The error wrapper, prompt, token count, discovery, live allowed list, token audience and kill switch come from Spell's server (`workspace/spell`). The example-input table, tool-choice eval, split CI and `.mcp.json` come from the DSSG datapool server, where rewritten descriptions raised Haiku's correct tool choice from 83% to 96%.
