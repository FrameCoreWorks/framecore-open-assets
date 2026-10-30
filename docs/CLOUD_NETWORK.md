# Running Open Assets in a cloud container

Cloud and sandboxed agent containers (for example Claude Code on the web, the Claude app's cloud projects
and other hosted shells) often allow only package registries and GitHub. Provider hosts are then refused
by the container's own network policy before any request reaches the provider, and searches fail.

## Check first

```bash
python3 plugins/framecore-open-assets/scripts/runtime.py reach
```

`reach` opens one connection to port 443 of every provider host (through the container's proxy when one is
set) and closes it; providers receive no HTTP request. It reports each provider as `reachable`, `blocked`,
`unreachable` or `unknown`, lists `ready_providers`, `blocked_domains` and the full `allowlist`, and adds
`advice` when anything is blocked. A search that hits the same policy fails with `network_blocked`
instead of a generic `transport_error`.

## Allow the provider hosts

`runtime.py domains` prints the allowlist, one host per line, generated from `providers.json` (a leading
`*.` covers every subdomain). For version 0.4.0 it is:

```text
commons.wikimedia.org
upload.wikimedia.org
thumb.wikimedia.org
collectionapi.metmuseum.org
images.metmuseum.org
openaccess-api.clevelandart.org
openaccess-cdn.clevelandart.org
data.rijksmuseum.nl
id.rijksmuseum.nl
iiif.micr.io
www.loc.gov
tile.loc.gov
lcweb2.loc.gov
images-api.nasa.gov
images-assets.nasa.gov
librivox.org
archive.org
*.archive.org
api.finna.fi
www.finna.fi
museo.disec.fi
api.wellcomecollection.org
iiif.wellcomecollection.org
ambientcg.com
*.ambientcg.com
acg-download.struffelproductions.com
api.phylopic.org
images.phylopic.org
api.polyhaven.com
dl.polyhaven.org
api.smk.dk
iip-thumb.smk.dk
iip.smk.dk
sfxmint.com
```

In a Claude Code cloud project: open Project settings, open the Cloud environment menu and choose Add
cloud environment (it is then selected for the project). Under Network access choose Custom, tick
"Also include default list of common package managers" so dependency installs keep working, paste the
list into Allowed domains and save. GitHub stays reachable at every level. The Claude Code documentation
says existing sessions of an Anthropic-hosted environment follow the change within about a minute
(https://code.claude.com/docs/en/cloud-environments#network-access, read 2026-10-30).

Other hosts have their own network settings. Where none can be changed, work on a computer with open
internet, or continue with your own files or assets made in code.

Evidence: on 2026-10-30, in a Claude Code cloud container with the default network policy, `reach`
reported `network: blocked` with all 32 probed hosts refused, and a Commons search returned
`network_blocked`. Behaviour after an allowlist change: NOT_RUN.
