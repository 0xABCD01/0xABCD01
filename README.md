<p align="center">
  <img
    src="./assets/profile-banner.svg"
    alt="A constellation graph in navy, cream, lavender, sage, and gold, with the handle set in monospace"
    width="100%"
  >
</p>

<p align="center">
  <img src="./assets/roles.svg" alt="Areas of work: bug bounty, pentest, OSINT" width="410">
</p>

# Hafiar

Bug hunter, pentester, and OSINT investigator. I reproduce published vulnerabilities, run authorized engagements, and build the tools I would otherwise write by hand. I also audit open-source libraries and send the fixes upstream.

Personal site: [0xabcd01.github.io](https://0xabcd01.github.io)

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1200&color=20304D&center=true&vCenter=true&width=600&lines=Breaking+things+locally%2C+politely.;Sending+the+fixes+upstream.;Reading+changelogs+so+you+don%27t+have+to." alt="Breaking things locally, politely. Sending the fixes upstream. Reading changelogs so you don't have to.">
</p>

<p align="center">
  <img src="./assets/divider.svg" alt="" width="560">
</p>

<p align="center">
  <img src="./assets/radar.svg" alt="An animated radar sweep with contacts lighting up as the beam passes them" width="180">
</p>

## <img src="./assets/icon-research.svg" width="20" height="20" align="left" alt=""> Research

| Advisory | What it is | Score |
|---|---|---|
| [CVE-2026-41089](https://github.com/0xABCD01/CVE-2026-41089) | Netlogon CLDAP stack buffer overflow. One unauthenticated UDP packet to a domain controller. | CVSS 9.8, CWE-121 |
| [CVE-2026-48866](https://github.com/0xABCD01/CVE-2026-48866) | Gravity Forms path traversal into arbitrary file deletion. | CVSS 9.6, CWE-22 |
| [SA-CORE-2026-014](https://github.com/0xABCD01/drupal-11.4.9-vuln-lab) | Drupal `field_ui` render-array callback. RCE once a contributed module is in play. | Drupal 11.4.9, fixed in 11.4.10 |

The [Drupal lab](https://github.com/0xABCD01/drupal-11.4.9-vuln-lab) covers all three core advisories that 11.4.9 shipped with, including the two stored XSS issues. Every proof of concept runs against a local container, never a third-party host.

## <img src="./assets/icon-code.svg" width="20" height="20" align="left" alt=""> Open source

62 pull requests across 34 projects: **31 merged**, **31 open**.

### Merged (31)

| Project | Contribution |
|---|---|
| symfony/symfony | [Strip the byte order mark at the start of a YAML stream](https://github.com/symfony/symfony/pull/67735) |
| symfony/symfony | [Skip empty lines when decoding CSV in the Serializer](https://github.com/symfony/symfony/pull/67752) |
| symfony/symfony | [Fix Glob patterns whose bracket expression contains a slash](https://github.com/symfony/symfony/pull/67785) |
| projectdiscovery/dsl | [Return errors instead of panicking on negative repeat counts and substr starts](https://github.com/projectdiscovery/dsl/pull/368) |
| projectdiscovery/nuclei | [Bump govaluate and antchfx/xpath past two template panics](https://github.com/projectdiscovery/nuclei/pull/7998) |
| projectdiscovery/nuclei | [Add a regression test for the govaluate string concatenation bug](https://github.com/projectdiscovery/nuclei/pull/8013) |
| symfony/ux | [Let LiveComponent collections contain null items during (de)hydration](https://github.com/symfony/ux/pull/4194) |
| WordPress/sqlite-database-integration | [Quote SQLite identifiers in LOCK TABLES, SHOW TABLES, and compound-PK indexes](https://github.com/WordPress/sqlite-database-integration/pull/599) |
| thedotmack/claude-mem | [Keep the doc_type filter out of the semantic search fallback query](https://github.com/thedotmack/claude-mem/pull/5355) |
| thedotmack/claude-mem | [Park queued messages at the process hard cap instead of discarding them](https://github.com/thedotmack/claude-mem/pull/5388) |
| thedotmack/claude-mem | [Persist SessionStart toggles and accept zero context counts via POST /api/settings](https://github.com/thedotmack/claude-mem/pull/5393) |
| thedotmack/claude-mem | [Discard a stalled session's buffered work once its resumes are spent](https://github.com/thedotmack/claude-mem/pull/5414) |
| thedotmack/claude-mem | [Keep context reads working when the WAL index cannot be established](https://github.com/thedotmack/claude-mem/pull/5432) |
| thedotmack/claude-mem | [Run the My Work refresh on the configured provider's agent first](https://github.com/thedotmack/claude-mem/pull/5436) |
| thedotmack/claude-mem | [Ship better-auth in the plugin install and create its auth tables](https://github.com/thedotmack/claude-mem/pull/5455) |
| thedotmack/claude-mem | [Fall back to the system locale for My Work focus areas when the text language setting is empty](https://github.com/thedotmack/claude-mem/pull/5669) |
| thedotmack/claude-mem | [Migrate stale PreToolUse/PreInvocation hooks in place on Antigravity](https://github.com/thedotmack/claude-mem/pull/5670) |
| thedotmack/claude-mem | [Drop unverifiable quotes from a fresh save instead of refusing it whole](https://github.com/thedotmack/claude-mem/pull/5992) |
| thedotmack/claude-mem | [Enforce mode filters on server context rows](https://github.com/thedotmack/claude-mem/pull/5993) |
| openai/codex-security | [Recheck empty targets before a resumed scan's first dispatch](https://github.com/openai/codex-security/pull/2346) |
| caddyserver/caddy | [Reject Caddyfile site blocks with unbalanced braces](https://github.com/caddyserver/caddy/pull/8375) |
| vimeo/psalm | [Stop a nullsafe call compared to a bool literal narrowing its receiver to null](https://github.com/vimeo/psalm/pull/13602) |
| thedotmack/claude-mem | [Name the run's language in the goals step's questions too](https://github.com/thedotmack/claude-mem/pull/6187) |
| ClickHouse/ClickHouse | [Make equal ClickHouseVersion objects hash equal so set and dict lookups dedupe them](https://github.com/ClickHouse/ClickHouse/pull/129594) |
| ClickHouse/ClickHouse | [Honor glob excludes and not_exists_ok in praktika path traversal for job digests](https://github.com/ClickHouse/ClickHouse/pull/129595) |
| thedotmack/claude-mem | [Write the My Work build story in parts so it stays under the question budget](https://github.com/thedotmack/claude-mem/pull/6279) |
| thedotmack/claude-mem | [Finish setup locally when the prompt history exceeds the hosted upload cap](https://github.com/thedotmack/claude-mem/pull/6280) |
| thedotmack/claude-mem | [Log failed folder CLAUDE.md updates and retry them on the next observation](https://github.com/thedotmack/claude-mem/pull/6208) |
| thedotmack/claude-mem | [Detect the legacy shell alias in install/update/doctor and warn when the worker runs outside the resolved plugin root](https://github.com/thedotmack/claude-mem/pull/6300) |
| thedotmack/claude-mem | [Stop the cache sweep pruning a version folder whose recorded Claude process is still alive](https://github.com/thedotmack/claude-mem/pull/6352) |
| grafana/loki | [Drain the pattern aggregation buffer on Stop so buffered patterns survive shutdown](https://github.com/grafana/loki/pull/26663) |

### Open (31)

| Project | Contribution |
|---|---|
| WordPress/sqlite-database-integration | [Split MySQL Proxy result packets at the maximum packet length](https://github.com/WordPress/sqlite-database-integration/pull/601) |
| WordPress/sqlite-database-integration | [Pass workflow values via env in release workflows](https://github.com/WordPress/sqlite-database-integration/pull/604) |
| pypi/warehouse | [Fix footer color contrast and landmark coverage](https://github.com/pypi/warehouse/pull/20882) |
| pypi/warehouse | [Make search-button focus visible and stop the classifier filter trapping keyboard focus](https://github.com/pypi/warehouse/pull/20884) |
| pypi/inspector | [Normalize archive member names so bad directory entries are browsable](https://github.com/pypi/inspector/pull/336) |
| Panniantong/agent-reach | [Treat an all-NOT_FOUND live test as a stale sample, not a broken channel](https://github.com/Panniantong/agent-reach/pull/909) |
| huggingface/transformers | [Fix CLAP loss double-counting the text-to-audio direction](https://github.com/huggingface/transformers/pull/50319) |
| dwisiswant0/apkleaks | [Stop the IP address pattern truncating the last octet](https://github.com/dwisiswant0/apkleaks/pull/107) |
| dwisiswant0/apkleaks | [Stop the CTF flag pattern matching plain CSS rules](https://github.com/dwisiswant0/apkleaks/pull/108) |
| anthropics/claude-quickstarts | [Continue paused server-tool turns instead of returning them unfinished](https://github.com/anthropics/claude-quickstarts/pull/533) |
| anomalyco/opencode | [Do not reuse an unmigrated V1 session ID on create](https://github.com/anomalyco/opencode/pull/62014) |
| micropython/micropython | [Support converting int subclass instances to float](https://github.com/micropython/micropython/pull/19904) |
| charmbracelet/x | [Stop the ANSI decoder panicking on sequences with more than 32 parameters](https://github.com/charmbracelet/x/pull/1040) |
| sherlock-project/sherlock | [Stop usernames escaping the output folder in result filenames](https://github.com/sherlock-project/sherlock/pull/3211) |
| google/go-containerregistry | [Write cached layers via a temporary file so concurrent readers never see a partial layer](https://github.com/google/go-containerregistry/pull/2505) |
| elastic/beats | [Report queue filled.pct as 0 when the queue has no finite limit](https://github.com/elastic/beats/pull/54652) |
| caddyserver/certmagic | [Wait for an in-flight managed certificate load before failing a handshake](https://github.com/caddyserver/certmagic/pull/429) |
| PHP-CS-Fixer/PHP-CS-Fixer | [Run BracesFixer after MethodArgumentSpaceFixer so ensure_fully_multiline signatures converge in one run](https://github.com/PHP-CS-Fixer/PHP-CS-Fixer/pull/9950) |
| projectdiscovery/nuclei-templates | [Add an active-probe template for CVE-2026-129289, PHP-FPM request smuggling via an unread request body](https://github.com/projectdiscovery/nuclei-templates/pull/18049) |
| DataDog/helm-charts | [Use the OpenMetrics V2 check config for datadog-operator metrics](https://github.com/DataDog/helm-charts/pull/3096) |
| thedotmack/claude-mem | [Keep truncated My Work answers for diagnosis, fix the limit error's advice, and let focus skip a request](https://github.com/thedotmack/claude-mem/pull/6441) |
| openai/tiktoken | [Stop redact.py skipping tracked files with non-ASCII names](https://github.com/openai/tiktoken/pull/646) |
| anthropics/claude-quickstarts | [Return the real error from the customer-support chat route and show it in the chat UI](https://github.com/anthropics/claude-quickstarts/pull/568) |
| cloudflare/cloudflared | [Keep the service token file when a Linux service install fails](https://github.com/cloudflare/cloudflared/pull/1806) |
| cloudflare/pingora | [Preserve HTTP version and reason phrase in HeaderSerde round-trips](https://github.com/cloudflare/pingora/pull/1146) |
| NVIDIA/NVSentinel | [Classify NICs by PCI address so RDMA renames cannot swap roles](https://github.com/NVIDIA/NVSentinel/pull/2522) |
| google/adk-go | [Replay empty-text thinking blocks as thinking instead of redacted_thinking](https://github.com/google/adk-go/pull/2488) |
| google/xmc | [Persist STOPPED when a deleting JobSet's stored execution is STOPPING](https://github.com/google/xmc/pull/1764) |
| GoogleCloudPlatform/k8s-aibom | [Require the verifier module by version and drop the root replace directive](https://github.com/GoogleCloudPlatform/k8s-aibom/pull/422) |
| anthropics/claude-quickstarts | [Detect Web Component radios in browser snapshots and refuse clicks on disabled elements](https://github.com/anthropics/claude-quickstarts/pull/569) |
| cloudflare/pingora | [Flush HTTP/1 Content-Length bodies after each write](https://github.com/cloudflare/pingora/pull/1147) |

<p align="center">
  <img src="./assets/bug-walk.svg" alt="A small bug walking a dotted path" width="560">
</p>

<p align="center">
  <img height="180" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=0xABCD01" alt="GitHub statistics for 0xABCD01">
  <img height="180" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=0xABCD01" alt="Top languages by repository">
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=0xABCD01&background=FBF3E4&stroke=E4D6B8&ring=C9962E&fire=C9962E&currStreakLabel=20304D&sideLabels=3A3A3A&currStreakNum=20304D&sideNums=20304D&dates=6B6B6B" alt="Contribution streak">
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=0xABCD01&bg_color=FBF3E4&color=20304D&line=C9962E&point=B8935A&area=true&hide_border=true" alt="Contribution activity graph for 0xABCD01" width="820">
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/0xABCD01/0xABCD01/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/0xABCD01/0xABCD01/output/github-contribution-grid-snake.svg">
    <img alt="A snake eating its way through the contribution graph" src="https://raw.githubusercontent.com/0xABCD01/0xABCD01/output/github-contribution-grid-snake.svg">
  </picture>
</p>

## <img src="./assets/icon-tools.svg" width="20" height="20" align="left" alt=""> Tools

| Repository | What it does |
|---|---|
| [agentlure](https://github.com/0xABCD01/agentlure) | Detonates MCP servers and agent skills against fake credentials in a sandbox, so a poisoned tool shows itself before you install it. |
| [test-amnesty](https://github.com/0xABCD01/test-amnesty) | Compares an edited pytest file against the original and catches tests that were weakened to pass. |
| [cachelint](https://github.com/0xABCD01/cachelint) | Predicts which Dockerfile layer busts the build cache and suggests a faster order. |
| [codex-skills](https://github.com/0xABCD01/codex-skills) | Workflow prompts for Codex CLI. Each one pins exact commands so the model cannot skip a step. |
| [cloud-file-manager](https://github.com/0xABCD01/cloud-file-manager) | Self-hosted file manager with encryption at rest, per-file permissions, and access logs. |
| [crystal-cavern](https://github.com/0xABCD01/crystal-cavern) | Puzzle game written in C++17 and compiled to WebAssembly, no runtime dependencies. [Play it](https://0xabcd01.github.io/crystal-cavern/). |

<p align="center">
  <img src="./assets/pulse.svg" alt="An animated signal line with two heartbeat spikes, a bright pulse travelling along it" width="560">
</p>

## <img src="./assets/icon-now.svg" width="20" height="20" align="left" alt=""> Currently

- Building reproductions for Drupal 11.4.x advisories, one repository per release.
- Auditing fresh open-source releases. Five reports are sitting with vendors and maintainers right now.
- Turning the parts of pentesting I repeat by hand into small tools.

<p align="center">
  <img src="./assets/constellation.svg" alt="An animated constellation: stars twinkle while a line draws itself between them, and a shooting star crosses now and then" width="100%">
</p>

## <img src="./assets/icon-contact.svg" width="20" height="20" align="left" alt=""> Contact

- X: [@VortexXzy](https://x.com/VortexXzy)
- Bug reports and questions: open an issue on the relevant repository.

<p align="center">
  <img src="https://readme-jokes.vercel.app/api?theme=default" alt="A random programming joke">
</p>

<p align="center">
  <img src="./assets/mark.svg" alt="" width="52">
</p>

<p align="center">
  <img src="./assets/waves.svg" alt="Three layered waves in sage, lavender, and gold drifting past each other" width="100%">
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=0xABCD01&style=flat-square&color=B8935A" alt="Profile view counter">
</p>
