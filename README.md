# Hermes Browserless Web Extract

Give your Hermes agent the ability to read any web page as a real browser would — powered by Browserless.io's headless Chrome infrastructure.

When your agent calls `web_extract(url)`, this plugin opens a real Chromium instance on Browserless's servers, waits for the page to fully render (including JavaScript, SPAs, lazy-loaded content), and returns the complete HTML back to your agent. It's the difference between downloading a skeleton and seeing the actual page.

## Why use this plugin?

**Real browser rendering.** A plain HTTP GET request misses everything JavaScript generates — single-page apps, dynamic content, lazy-loaded images, client-side navigation. Browserless runs a real headless Chrome that executes every `<script>` tag, applies every CSS animation, and loads every deferred resource. What you get back is what a human sees.

**No browser infrastructure to manage.** You don't install Chrome, Chromium, or Puppeteer on your machine. You don't manage browser processes, memory limits, or headless flags. Browserless runs the browsers on their infrastructure. You send a simple REST request and get HTML back. The plugin handles all the HTTP plumbing.

**JavaScript-heavy sites work.** Documentation sites, blogs, forums, and marketing pages that rely on client-side rendering (React, Vue, Svelte, Next.js, etc.) are invisible to basic HTTP fetchers. Browserless renders them fully. This is especially important for modern technical content — many API docs, changelogs, and RFC pages are SPAs.

**Extract-only by design.** This plugin does one thing: fetch rendered HTML from a URL. It doesn't search. It doesn't summarize. It hands the raw page content to Hermes, which can then reason over it, summarize it, or compare it against other sources. Pair it with a search provider (like the Gemini web search plugin, Brave, or SearXNG) and each tool does its job well.

**Graceful error handling.** Every URL gets either content or a clear error message. Network timeouts, HTTP 4xx/5xx responses, empty pages — all handled per-URL, so one bad link never kills an entire batch extraction.

**Zero-code configuration.** Set two environment variables, add a few lines to your config file, and restart. There's no SDK to initialize, no browser flags to tune, and no Puppeteer scripts to write.

## What is Browserless?

[Browserless.io](https://browserless.io) is a hosted headless browser service. They run and manage Chromium instances in the cloud so you don't have to. You send HTTP requests describing what you want (a screenshot, a PDF, a page's rendered HTML) and they handle the browser lifecycle — launching, navigating, waiting for render, and tearing down.

Their `/content` REST endpoint (which this plugin uses) takes a URL and returns the fully-rendered HTML. It's the simplest possible interface: POST a URL, get back HTML. No WebSocket connections, no CDP protocol, no browser management code.

Key features of Browserless:

- **Real Chrome/Chromium instances** — not a lightweight emulation, not a DOM parser guessing at JS output
- **Configurable wait strategies** — wait for specific selectors, events, timeouts, or functions before returning
- **Resource blocking** — skip images, fonts, and media for faster extraction
- **Stealth mode and proxy support** — for sites with basic bot detection
- **Free tier available** — start without a credit card

## What you'll need

- **Hermes agent** installed and working (any platform — CLI, desktop, Telegram, Discord, etc.)
- **A Browserless.io account** (free to start, takes 2 minutes)
- **Your Browserless API token** (from the dashboard)
- **Your Browserless instance URL** (provided at signup, or use the shared default)

That's it. No other accounts, no browser installs, no headless flags to debug.

## Getting a Browserless account and token

1. Go to **[browserless.io](https://browserless.io/)** in your browser
2. Click **"Get Started"** or **"Sign Up"**
3. Create an account (email + password, or GitHub/Google SSO)
4. Once logged in, go to the **[Account page](https://browserless.io/account/)**
5. Under **API Tokens**, copy your token — it will look like a long random string
6. Under **Service Domain**, note your instance URL. It usually looks like `https://production-sfo.browserless.io`

The free tier gives you a limited number of concurrent sessions and monthly usage hours. You'll know if you need to upgrade — Browserless will email you when you approach the limit.

**Important:** Treat your API token like a password. Anyone with it can launch browsers on your behalf and consume your usage quota. Don't commit it to git, don't paste it into chat logs, and don't share it publicly.

## Installation

### One command (recommended)

From inside your Hermes environment's virtual environment:

```bash
pip install hermes-browserless-web-extract
```

This pulls the plugin from PyPI and installs its sole dependency (`httpx`).

### From source

```bash
git clone https://github.com/your-username/hermes-browserless-web-extract.git
cd hermes-browserless-web-extract
pip install .
```

### Editable install (for development)

```bash
git clone https://github.com/your-username/hermes-browserless-web-extract.git
cd hermes-browserless-web-extract
pip install -e .
```

An editable install means changes you make to the source code are picked up immediately without reinstalling. Use this if you plan to modify or contribute to the plugin.

## Configuration

Everything happens in two files inside your `~/.hermes/` directory. No code changes, no init scripts, no environment hacks.

### Step 1 — Add your credentials

Create or open `~/.hermes/.env` in any text editor.

Add these two lines:

```bash
BROWSERLESS_TOKEN=your-api-token-here
BROWSERLESS_URL=https://production-sfo.browserless.io (or your local URL)
```

**What these mean:**

- `BROWSERLESS_TOKEN` — Your Browserless API token. Required. This is how Browserless knows you're a paying (or free-tier) customer and tracks your usage.
- `BROWSERLESS_URL` — The base URL of your Browserless instance. Defaults to `https://production-sfo.browserless.io` if not set. If you purchased a dedicated instance or signed up through a regional endpoint, use that URL instead. If you self-host Browserless, point this at your own server.

**Gotchas to avoid:**

- Do not wrap values in quotes (`BROWSERLESS_TOKEN="abc"` — wrong, the quotes become part of the value)
- Do not add spaces around the `=` sign (`BROWSERLESS_TOKEN = abc` — wrong)
- Do not reuse tokens from other services. Browserless tokens are specific to Browserless.
- Make sure the `.env` file is plain text, not rich text (use Notepad, vim, nano, or VS Code — not Word or TextEdit in rich mode)

### Step 2 — Enable the plugin

Open `~/.hermes/config.yaml` in any text editor. Add `hermes-browserless-web-extract` to the `plugins.enabled` list:

```yaml
plugins:
  enabled:
    - hermes-browserless-web-extract
```

If you already have other plugins enabled, add this one to the existing list:

```yaml
plugins:
  enabled:
    - some-other-plugin
    - hermes-browserless-web-extract
```

If no `plugins` section exists yet in your config, create it at the top level of the file:

```yaml
# ... other config options above ...

plugins:
  enabled:
    - hermes-browserless-web-extract

# ... other config options below ...
```

### Step 3 — Tell Hermes to use Browserless for extraction

In the same `config.yaml`, under the `web` section, set the extract backend to `browserless`:

```yaml
web:
  extract_backend: browserless
```

Here's what a complete `config.yaml` might look like after setup (your file will have its own sections — that's fine, you only need to add the `plugins` and `web` parts):

```yaml
plugins:
  enabled:
    - hermes-browserless-web-extract

web:
  extract_backend: browserless
```

### Step 4 — Restart Hermes

Quit your Hermes agent completely and restart it. On the next question that triggers a `web_extract` call, the agent will use Browserless.

Plugin discovery happens at startup. If you don't restart, Hermes won't see the new plugin.

## Verifying it works

The quickest test is to ask your agent to extract a page that uses JavaScript:

```
> extract the content of https://news.ycombinator.com

> what does https://react.dev/learn say on the first page?

> read and summarize https://docs.python.org/3/whatsnew/3.13.html
```

If the agent returns current, rendered content with clear structure, the plugin is working.

You can also check from the Hermes tools picker:

```bash
hermes tools
```

Navigate to **Web Extract** — you should see **Browserless** listed with a green checkmark and the "API key required" badge.

### What success looks like

The agent should be able to read and reason about the actual page content — headings, paragraphs, code blocks, links — not just metadata or title tags. If you ask "what are the top 5 stories on Hacker News?" and the agent can list them, it's working.

### What to expect from JavaScript-heavy pages

Some pages take a few seconds to fully render. This is normal. The plugin waits up to 30 seconds (configurable) for the page to settle before returning the HTML. If a page is particularly slow, you might notice a small delay, but the content should be complete.

## How it works

When your agent calls `web_extract("https://example.com")`, here's what happens:

1. **Hermes dispatches to this plugin.** It looks up the active extract backend (`browserless`) and calls `provider.extract(["https://example.com"])`.
2. **The plugin builds a request.** It takes your token and URL, constructs a POST to `$BROWSERLESS_URL/content?token=$BROWSERLESS_TOKEN`, and sends a JSON body with the target URL plus browser configuration (timeout, resource blocking).
3. **Browserless launches a headless Chrome instance.** On their infrastructure, a real Chromium process starts. It navigates to the URL, executes all JavaScript, waits for network requests to settle, and captures the final DOM state.
4. **The rendered HTML is returned.** Browserless sends back the complete `<html>...</html>` string — not just the initial server response, but the fully rendered page including all JS-generated content.
5. **The plugin passes it to Hermes.** The HTML is returned in the standard extract result format, with the URL, title, raw content, and metadata. Hermes can then feed it to the LLM for summarization, comparison, or any other reasoning task.

The raw HTTP request looks like this:

```
POST https://production-sfo.browserless.io/content?token=YOUR_TOKEN
Content-Type: application/json

{
  "url": "https://example.com",
  "waitForTimeout": 30000,
  "bestAttempt": true,
  "rejectResourceTypes": ["image", "media", "font"],
  "rejectRequestPattern": [".*\\.(png|jpg|jpeg|gif|webp|svg|ico|css|woff2?).*"]
}
```

**Why block images?** Text extraction doesn't need images, fonts, CSS, or media files. Blocking them makes pages load faster and reduces bandwidth — you get the same HTML content in less time. If you ever need to extract images (e.g., for vision-capable models), you can override this behavior by setting `rejectResourceTypes` to an empty list (see [Advanced configuration](#advanced-configuration)).

## Using alongside other web plugins

This plugin is **extract-only**. It does not search the web — it only fetches content from URLs you already have.

This is intentional. You can pair it with a search provider for a complete web pipeline:

### Example: Gemini for search, Browserless for extract

```yaml
plugins:
  enabled:
    - hermes-gemini-web-search
    - hermes-browserless-web-extract

web:
  search_backend: gemini
  extract_backend: browserless
```

With this setup, when your agent needs to find something, Gemini searches Google and returns results. When it wants to read a specific page, Browserless fetches the fully-rendered HTML.

### Example: Brave for search, Browserless for extract

```yaml
plugins:
  enabled:
    - hermes-brave-web-search
    - hermes-browserless-web-extract

web:
  search_backend: brave-free
  extract_backend: browserless
```

Any search provider (Brave, SearXNG, Tavily, Firecrawl, Gemini) can be paired with Browserless for extraction. The plugins are independent and Hermes routes each tool call to the right provider.

### Using a single backend for both

If you have a provider that does both search and extract (like Firecrawl or Gemini), you can use `web.backend` as a shared default and override just one capability. For example, use Firecrawl for everything but Browserless for extract on JS-heavy pages:

```yaml
web:
  backend: firecrawl
  extract_backend: browserless
```

## Advanced configuration

### Extraction timeout

Control how long Browserless waits for the page to fully render before returning whatever HTML is available. Default is 30000 ms (30 seconds):

```yaml
web:
  extract_backend: browserless
  browserless_timeout: 60000
```

Increase this for slow-loading pages (e.g., SPAs with heavy data fetching). Decrease it if you prefer faster-but-maybe-incomplete results.

Note: The value is in milliseconds. Common settings:

- `10000` — 10 seconds, for fast static pages
- `30000` — 30 seconds, the default, works for most pages
- `60000` — 60 seconds, for heavy SPAs or rate-limited APIs
- `120000` — 2 minutes, rarely needed, for very slow backends

### Custom Browserless instance URL via config

Instead of setting `BROWSERLESS_URL` in `.env`, you can set it in `config.yaml`:

```yaml
web:
  extract_backend: browserless
  browserless_url: https://my-custom-instance.browserless.io
```

The environment variable takes precedence over the config file value, which makes `.env` the preferred place for secrets and the config file the right place for instance-specific overrides.

### Running browserless locally (self-hosted)

If you run Browserless via Docker on your own machine:

```yaml
web:
  extract_backend: browserless
  browserless_url: http://localhost:3000
```

With matching `.env`:

```bash
BROWSERLESS_TOKEN=  # can be empty for local instances without auth
BROWSERLESS_URL=http://localhost:3000
```

### Per-capability routing

Browserless can be used as the shared backend for both search and extract, even though it only supports extract. Hermes will fall back gracefully for search:

```yaml
web:
  backend: browserless
```

This works: search calls will fail with a clear error, extract calls will work normally. For better UX, explicitly set `search_backend` to a provider that supports search and `extract_backend` to browserless.

## Troubleshooting

### "BROWSERLESS_TOKEN environment variable not set"

The plugin can't find your API token. Check that:

1. `~/.hermes/.env` exists and contains a line starting with `BROWSERLESS_TOKEN=`
2. There are no extra spaces or quotes around the value (correct: `BROWSERLESS_TOKEN=abc123`, incorrect: `BROWSERLESS_TOKEN="abc123"` or `BROWSERLESS_TOKEN = abc123`)
3. You restarted Hermes after adding the key (environment variables are read at startup)
4. The file has a trailing newline (some editors strip it; add a blank line at the end to be safe)

If you've verified all of the above and it still fails, try setting the variable directly in your shell before launching Hermes:

```bash
export BROWSERLESS_TOKEN=your-token-here
hermes
```

This bypasses the `.env` file entirely and confirms the variable is set in the process environment.

### "BROWSERLESS_URL not set" or connection failures

If you got the token right but requests fail to connect:

1. Verify you set `BROWSERLESS_URL` in `.env` (or `browserless_url` in `config.yaml`)
2. If using the default (`https://production-sfo.browserless.io`), make sure that domain is reachable from your network: `curl -I https://production-sfo.browserless.io`
3. If using a custom instance URL, verify it starts with `https://` or `http://`

### "Browserless HTTP 401: Unauthorized"

Your token is invalid, expired, or missing. Get a new one from the [Browserless account page](https://browserless.io/account/). Tokens can be rotated from the dashboard — if you previously rotated your token, the old one stops working immediately.

Also check: the token is passed as a query parameter (`?token=...`), not as an `Authorization` header. If you're inspecting the request, you should see the token in the URL, not in the headers.

### "Browserless HTTP 403: Forbidden"

Your account doesn't have access to the requested resource. Common causes:

- You're on the free tier and have exceeded your concurrent session limit. Wait a moment and retry.
- Your account is in a trial period that has expired. Check the Browserless dashboard for account status.
- You're using a dedicated instance URL but sending requests through the shared endpoint, or vice versa.

### "Browserless returned empty content"

The page may have blocked the headless browser, or the page finished loading before any content was rendered. Try:

1. **Increase the timeout.** Add `browserless_timeout: 60000` to your `config.yaml` to give the page more time to render.
2. **Check the page manually.** Open the URL in your own browser. Does it load? Does it require login? Is it behind a paywall or CAPTCHA?
3. **Try the /unblock endpoint.** Browserless has an unblock API for sites with bot detection. This plugin uses `/content` by default. For heavily-protected sites, you may need a different Browserless endpoint or a more sophisticated extraction tool.
4. **Check if the site blocks headless browsers.** Some sites (major social media platforms, banks, ticket vendors) aggressively detect and block automated browsers. Browserless handles basic protections, but sophisticated anti-bot systems may still succeed. For these cases, consider using the official API of the site or accepting that extraction won't work.

### The agent is not using the plugin

1. Did you restart Hermes after making configuration changes? Plugin discovery happens at startup — changes to `config.yaml` are not picked up dynamically.
2. Check that `hermes-browserless-web-extract` is listed under `plugins.enabled` in `config.yaml`. A missing entry means the plugin is installed but inactive.
3. Check that `web.extract_backend` is set to `browserless`. If it's set to something else, that provider handles extraction instead.
4. Run `hermes tools` and look under the Web Extract section. If Browserless isn't listed, the plugin isn't being discovered — check the installation.

### "hermes-browserless-web-extract is not enabled"

Hermes found the plugin package but hasn't been told to activate it. Add it to your config:

```yaml
plugins:
  enabled:
    - hermes-browserless-web-extract
```

Then restart Hermes. The message should disappear.

### "Could not import hermes_browserless_web_extract"

The plugin isn't installed in your active Python environment. Verify:

```bash
pip show hermes-browserless-web-extract
```

If nothing shows up, install it:

```bash
pip install hermes-browserless-web-extract
```

If you're using a virtual environment for Hermes, make sure you're installing into that same environment. Run `which python` or `which pip` to confirm you're in the right one.

## Development

### Setup

```bash
git clone https://github.com/your-username/hermes-browserless-web-extract.git
cd hermes-browserless-web-extract
pip install -e .
```

### Running tests

```bash
pytest
```

Tests use mocks — no API token or network access is needed to run the test suite. The tests verify:

- Provider availability detection (both env vars present, only one, neither)
- Capability flags (search disabled, extract enabled)
- Successful extraction (mocked HTTP response)
- Multi-URL extraction (batch correctness)
- Error handling (missing token, HTTP errors, empty responses)

### Project structure

```
hermes-browserless-web-extract/
├── pyproject.toml                           # Package metadata and build config
├── README.md
├── LICENSE
├── .gitignore
├── hermes_browserless_web_extract/
│   ├── __init__.py                          # Plugin entry point (calls register)
│   └── provider.py                          # BrowserlessWebExtractProvider class
├── tests/
│   ├── __init__.py
│   └── test_browserless_provider.py         # Unit tests
```

### How the plugin integrates with Hermes

1. **Entry point:** `pyproject.toml` declares `[project.entry-points."hermes_agent.plugins"]` pointing to the package. Hermes discovers plugins via setuptools entry points.
2. **Registration:** `__init__.py` calls `register(ctx)` which calls `ctx.register_web_search_provider(...)` with an instance of `BrowserlessWebExtractProvider`.
3. **Provider class:** `provider.py` subclasses `WebSearchProvider` from `agent.web_search_provider` and implements the required interface: `name`, `display_name`, `is_available()`, `supports_extract()`, `extract()`, and `get_setup_schema()`.
4. **Dispatching:** When Hermes needs to call `web_extract`, it looks up the active extract backend, finds this provider, and calls `extract(urls)`.

## License

MIT — see the [LICENSE](LICENSE) file for details.
