# Reference-only sources

These sources help a user look, compare and describe: moodboards, style research and reference packs. They are
**not** asset providers. Nothing here is licensed for use in finished work, nothing passes the rights gates of
[the contract](contract.md), and none of it is in `providers.json`, `search`, `verify` or `download`. Keep their files
apart from licensed assets and never write an `.asset.json` sidecar for them.

## Pinterest

- Route: the optional Pinterest connector, FrameCore Works Toolbox entry `pinterest-references` (a pinned local MCP
  server, `pinterest-mcp-server@1.2.0` by terryso, MIT). Its tools are `pinterest_search`,
  `pinterest_get_image_info` and `pinterest_search_and_download`. Open Assets never starts or calls it itself.
- It needs Google Chrome in its standard place and Node.js with npx; no account or key. ChatGPT Work cannot run it.
- Rights: every image belongs to its author or the site it was pinned from. Pinterest is reference only.

### When to use it

- A moodboard for a reel, ad or campaign.
- Style research: typography, colour, layout, composition, motion ideas.
- A reference pack handed to Creative Studio (`reference-pack-curator`) or to a designer.

Not for: a background, texture, photo, illustration or frame that will appear in delivered work. For those, search
the licensed providers in this plugin, or make the asset.

### How to save

1. Search with a few precise keyword queries, show the pins (title, pin link) and let the user pick.
2. Open each picked pin and read its author or original source; write `Unknown` when the page does not show it.
3. Save kept files into the project's `references/pinterest/` folder, never into the asset folders. Next to each
   file write `<file>.reference.json`:

```json
{
  "kind": "reference-only",
  "source": "pinterest",
  "pin_url": "https://www.pinterest.com/pin/...",
  "image_url": "https://i.pinimg.com/...",
  "title": "...",
  "author": "... or Unknown",
  "original_source": "URL the pin links to, or Unknown",
  "query": "...",
  "retrieved_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "rights": "Not cleared. Reference only; do not use in finished work.",
  "tool": "pinterest-mcp-server@1.2.0"
}
```

4. In the reply, say which pins were saved and that they are references only.

### When the connector is missing or fails

Say in one sentence that Pinterest references are not available here (not installed, no Chrome, or a block) and
continue: the user's own references, a written style description, or licensed providers for usable media. A
missing connector never stops an Open Assets task. Do not retry a blocked search in a loop, sign in for the user or
use proxies.
