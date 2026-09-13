<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="./assets/banner-light.svg" />
    <img
      src="./assets/banner-light.svg"
      width="100%"
      alt="Abstract banner of layered cream, sage and lavender arcs on a deep navy field with a fine gold rule"
    />
  </picture>
</p>

<h1 align="center">Hello — I'm [YOUR NAME].</h1>

<p align="center">
  <em>I find the bug everyone assumed was a feature, then build the tool that keeps it from coming back.</em>
</p>

<p align="center">
  Security researcher and developer-tools builder. I work in the space between offensive research
  and the unglamorous engineering that keeps systems honest.
</p>

<p align="center">
  <a href="https://github.com/0xABCD01">
    <img alt="GitHub profile" src="https://img.shields.io/badge/GitHub-0xABCD01-232838?style=flat-square&logo=github&logoColor=F7F2E7" />
  </a>
  <a href="https://x.com/VortexXzy">
    <img alt="X profile" src="https://img.shields.io/badge/X-@VortexXzy-18253D?style=flat-square&logo=x&logoColor=F7F2E7" />
  </a>
  <img alt="Current focus" src="https://img.shields.io/badge/focus-security_research_%26_tooling-8E86B8?style=flat-square" />
</p>

<p align="center">
  <img src="./assets/divider.svg" width="320" height="14" alt="" />
</p>

## A quick hello

Most of my work starts the same way. Something behaves oddly, the documentation stays quiet about it,
and nobody has written it down yet — so I write it down. As a proof of concept, a test suite, a
linter, or a README that finally explains the thing.

I would rather hand someone evidence than an opinion, and I would rather ship one small tool that
works than a large one that mostly does.

## About me

I work across application security, developer tooling, and privacy-minded software. My public
repositories are mostly Python and TypeScript, with a fair amount of Docker, GitHub Actions, and
test infrastructure holding it together.

Two of those repositories document vulnerabilities I researched responsibly — a Netlogon/CLDAP
buffer overflow and a Gravity Forms path traversal. The rest are the tools I built because I kept
running into the same problem by hand.

## Selected security research

**[CVE-2026-41089](https://github.com/0xABCD01/CVE-2026-41089)** — Netlogon CLDAP stack buffer overflow (CVSS 9.8)

The most-starred thing I have published. It includes a working proof of concept, affected-version
detail, and a clearly scoped safe-testing boundary so it stays useful for defenders and not just
for demos.

**[CVE-2026-48866](https://github.com/0xABCD01/CVE-2026-48866)** — Gravity Forms arbitrary file deletion via path traversal (CVSS 9.6)

A shorter write-up of the same discipline: reproduce it, document it, keep the blast radius
obvious to anyone who reads it first.

## Current focus

- Making weakened tests visible — a green build should mean something.
- Building developer tools that explain a problem instead of just failing.
- Designing privacy-conscious applications with explicit permissions and real audit trails.
- Writing technical work with reproducible examples and honest limitations.

## What I am building

**[test-amnesty](https://github.com/0xABCD01/test-amnesty)** — checks whether an edited test still
catches what it used to, by running the original and the edited version against the same
implementation.

**[cachelint](https://github.com/0xABCD01/cachelint)** — a zero-dependency Dockerfile linter that
predicts cache invalidation and suggests a faster layer order. Ten rules, twenty-four ecosystems.

**[cloud-file-manager](https://github.com/0xABCD01/cloud-file-manager)** — self-hosted file
management exploring encrypted storage, fine-grained permissions, and auditable access.

**[codex-skills](https://github.com/0xABCD01/codex-skills)** — structured prompts that push Codex
CLI to follow a workflow instead of guessing.

## Tech stack

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-2E4A6B?style=flat-square&logo=python&logoColor=F7F2E7" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-3D6285?style=flat-square&logo=typescript&logoColor=F7F2E7" />
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-A8823F?style=flat-square&logo=javascript&logoColor=F7F2E7" />
  <img alt="Shell" src="https://img.shields.io/badge/Shell-4E5A4A?style=flat-square&logo=gnubash&logoColor=F7F2E7" />
</p>

<p>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-5F7D74?style=flat-square&logo=fastapi&logoColor=F7F2E7" />
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-232838?style=flat-square&logo=next.js&logoColor=F7F2E7" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-3D6285?style=flat-square&logo=docker&logoColor=F7F2E7" />
  <img alt="pytest" src="https://img.shields.io/badge/pytest-4A6E8A?style=flat-square&logo=pytest&logoColor=F7F2E7" />
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub_Actions-4A5B78?style=flat-square&logo=github-actions&logoColor=F7F2E7" />
</p>

I prefer simple interfaces, reproducible experiments, readable code, and documentation that
respects the reader's time.

## GitHub activity

<p>
  <img alt="Stars on CVE-2026-41089" src="https://img.shields.io/github/stars/0xABCD01/CVE-2026-41089?style=flat-square&label=stars&color=B08D57&labelColor=232838" />
  <img alt="Forks of CVE-2026-41089" src="https://img.shields.io/github/forks/0xABCD01/CVE-2026-41089?style=flat-square&label=forks&color=8FA388&labelColor=232838" />
  <img alt="GitHub followers" src="https://img.shields.io/github/followers/0xABCD01?style=flat-square&label=followers&color=8E86B8&labelColor=232838" />
</p>

This account is young — I opened it in mid-2026 — and the graph above reflects focused bursts
around releases rather than daily noise. I would rather show four repositories I can defend in an
interview than forty I cannot.

## Learning journey

- Application security and authorization design.
- Evidence-driven testing and mutation analysis.
- Containerised systems and CI/CD reliability.
- Privacy, access control, and auditable infrastructure.

## A few things about how I work

- I read the README as part of the product, not after it.
- I like tools that show their evidence instead of asking for trust.
- One clear command usually beats ten decorative badges.
- My favourite kind of bug is the one that turns into a reusable tool.

## Find me

- **X** — [@VortexXzy](https://x.com/VortexXzy)
- **GitHub** — [0xABCD01](https://github.com/0xABCD01)
- **Project questions** — open an issue on the relevant repository; I read all of them.

<p align="center">
  <img src="./assets/divider.svg" width="320" height="14" alt="" />
</p>

<p align="center">
  Thanks for stopping by.
  <br />
  If something here was useful, an issue, a thoughtful review, or a small contribution
  is always the best way to say so.
</p>
