#!/usr/bin/env node
// Offline runner for nuclei JavaScript-protocol templates.
//
// Why this exists: the lab machine cannot download a nuclei release binary, so
// this shim re-implements the parts of the protocol the templates in this repo
// use, following the real implementation in projectdiscovery/nuclei:
//
//   * args are injected as globals into the JS runtime  (pkg/js/compiler/session.go)
//   * {{Host}}, {{Hostname}}, {{Port}} are derived from the input
//     (pkg/protocols/javascript/js.go executeWithResults)
//   * template `variables` are rendered with those values, and -var overrides
//     win over template variables          (render.Render + generators.MergeMaps)
//   * `success` is the truthiness of the script's last expression
//     (compiler.ExecuteWithOptions -> results.ToBoolean())
//   * pre-condition runs first; a falsy result skips the request
//   * matchers run against the resulting data map (part: response / host / matched)
//
// The HTTP client blocks inside the JS call, exactly like the Go client does,
// which is why http.Client calls work here without async/await.
//
// It is NOT nuclei: interactsh is not available (use --oob-log together with the
// lab listener to prove a blind callback), and the DSL/matcher surface is a
// documented subset.
//
// Usage:
//   node nuclei-shim.mjs <template.yaml> <target> [options]
//
// Options:
//   --var name=value     override/define a template variable (repeatable)
//   --print-response     print the script result (part: response)
//   --print-request      print each HTTP request the script makes
//   --dump-requests <dir>  save every request body (payload parity checks
//                        against the advisory's exploit.py)
//   --oob-log <path>     file the lab listener appends OOB hits to; new lines
//                        after the run satisfy interactsh_protocol matchers
//                        (lab stand-in for a real interactsh correlation)
//   --no-precondition    skip the pre-condition gate
//   --quiet              only print the verdict
//
// Exit codes: 0 = matched, 3 = not matched, 1 = error.
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import { createRequire } from 'node:module'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)

// node_modules is gitignored (and excluded from workspace snapshots), so give a
// usable error instead of "Cannot find module 'yaml'".
function harnessRequire(name) {
  try {
    return require(name)
  } catch (err) {
    if (err && err.code === 'MODULE_NOT_FOUND') {
      console.error(`harness dependency "${name}" is missing - run: cd lab/tools && npm install`)
      process.exit(1)
    }
    throw err
  }
}
const YAML = harnessRequire('yaml')

const HERE = path.dirname(fileURLToPath(import.meta.url))
const FETCHER = path.join(HERE, 'http-fetch.mjs')

const EXIT_MATCHED = 0
const EXIT_NOT_MATCHED = 3
const EXIT_ERROR = 1

// ------------------------------------------------------------------ CLI parsing
function parseArgs(argv) {
  const opts = { vars: {}, oobLog: '', printResponse: false, printRequest: false, precondition: true, quiet: false, dumpRequests: '' }
  const positional = []
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg === '--var') {
      const pair = argv[++i] || ''
      const eq = pair.indexOf('=')
      if (eq === -1) throw new Error(`--var expects name=value, got "${pair}"`)
      opts.vars[pair.slice(0, eq)] = pair.slice(eq + 1)
    } else if (arg === '--oob-log') {
      opts.oobLog = argv[++i] || ''
    } else if (arg === '--print-response') {
      opts.printResponse = true
    } else if (arg === '--print-request') {
      opts.printRequest = true
    } else if (arg === '--no-precondition') {
      opts.precondition = false
    } else if (arg === '--dump-requests') {
      opts.dumpRequests = argv[++i] || ''
    } else if (arg === '--quiet') {
      opts.quiet = true
    } else if (arg === '-h' || arg === '--help') {
      opts.help = true
    } else {
      positional.push(arg)
    }
  }
  opts.template = positional[0]
  opts.target = positional[1]
  return opts
}

const opts = parseArgs(process.argv.slice(2))
if (opts.help || !opts.template || !opts.target) {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').slice(1, 40).join('\n').replace(/^\/\/ ?/gm, ''))
  process.exit(opts.help ? 0 : EXIT_ERROR)
}

const say = (msg) => { if (!opts.quiet) console.log(msg) }
const problem = (msg) => console.error(msg)

// ------------------------------------------------------------ standard variables
// pkg/protocols/javascript/js.go: input -> getAddress() -> net.SplitHostPort()
function standardVariables(target) {
  let scheme = ''
  let rest = target
  const schemeMatch = target.match(/^([a-z][a-z0-9+.-]*):\/\//i)
  if (schemeMatch) {
    scheme = schemeMatch[1].toLowerCase()
    rest = target.slice(schemeMatch[0].length)
  }
  rest = rest.replace(/\/.*$/, '')

  let host = rest
  let port = ''
  const colon = rest.lastIndexOf(':')
  if (colon > 0 && !rest.includes(']')) {
    const candidate = rest.slice(colon + 1)
    if (/^[0-9]+$/.test(candidate)) {
      host = rest.slice(0, colon)
      port = candidate
    }
  }
  if (port === '') {
    if (scheme === 'https' || scheme === 'wss') port = '443'
    else if (scheme === 'http' || scheme === 'ws') port = '80'
  }

  return {
    Input: target,
    Host: host,
    Port: port,
    Hostname: port ? `${host}:${port}` : host,
    Scheme: scheme
  }
}

// ------------------------------------------------------------------ HTTP module
// Mirrors pkg/js/libs/http: Response{StatusCode,Body,Headers,URL,GetHeader},
// Client{Request,Get,Post,SetHeader}.
function makeHttpModule() {
  let requestSeq = 0

  function request({ Method, URL, Body, Headers, TimeoutSeconds, MaxBodyBytes }) {
    const method = String(Method || 'GET').toUpperCase()
    const headers = Object.assign({}, Headers || {})
    const timeoutMs = (Number(TimeoutSeconds) || 60) * 1000

    requestSeq += 1
    if (opts.dumpRequests && Body !== undefined && Body !== null) {
      fs.mkdirSync(opts.dumpRequests, { recursive: true })
      fs.writeFileSync(path.join(opts.dumpRequests, `${String(requestSeq).padStart(2, '0')}-${method}.bin`), String(Body))
    }
    if (opts.printRequest) {
      say(`[shim] #${requestSeq} ${method} ${URL} body=${Body === undefined || Body === null ? 0 : Buffer.byteLength(String(Body))}B`)
    }

    const payload = JSON.stringify({ method, url: String(URL), headers, body: Body === undefined || Body === null ? null : String(Body), timeoutMs })
    const run = spawnSync(process.execPath, [FETCHER], { input: payload, encoding: 'utf8', maxBuffer: 1 << 28 })
    if (run.status !== 0 || !run.stdout) {
      throw new Error(`connection failed: ${(run.stderr || 'request helper crashed').trim().slice(0, 200)}`)
    }
    const raw = JSON.parse(run.stdout)
    if (!raw.ok) {
      throw new Error(raw.error || 'connection failed')
    }
    const bytes = fs.readFileSync(raw.bodyFile)
    try { fs.unlinkSync(raw.bodyFile) } catch (err) { /* best effort */ }

    const maxBody = Number(MaxBodyBytes) || 0
    const buffer = maxBody > 0 && bytes.length > maxBody ? bytes.subarray(0, maxBody) : bytes
    const lowerHeaders = {}
    for (const [k, v] of Object.entries(raw.headers || {})) lowerHeaders[String(k).toLowerCase()] = v

    if (opts.printRequest) {
      say(`[shim] #${requestSeq} -> ${raw.status} ${raw.contentType || 'no content-type'} ${buffer.length}B`)
    }

    return {
      StatusCode: raw.status,
      Body: buffer.toString('utf8'),
      Headers: lowerHeaders,
      URL: String(URL),
      GetHeader(name) {
        return lowerHeaders[String(name).toLowerCase()] || ''
      }
    }
  }

  class Client {
    constructor() { this.headers = {} }
    SetHeader(name, value) { this.headers[String(name)] = String(value) }
    Request(request) { return request({ Headers: Object.assign({}, this.headers, request.Headers || {}), ...request }) }
    Get(url) { return request({ Method: 'GET', URL: url, Headers: Object.assign({}, this.headers) }) }
    Post(url, body) { return request({ Method: 'POST', URL: url, Body: body, Headers: Object.assign({}, this.headers) }) }
  }

  return {
    Client,
    Get: (url) => request({ Method: 'GET', URL: url }),
    Post: (url, body) => request({ Method: 'POST', URL: url, Body: body })
  }
}

// ---------------------------------------------------------------------- render
function renderText(text, values) {
  return String(text).replace(/\{\{([^}]+)\}\}/g, (marker, name) => {
    const key = name.trim()
    if (Object.prototype.hasOwnProperty.call(values, key)) return String(values[key])
    return marker // unknown markers ({{interactsh-url}} without interactsh) stay literal
  })
}

function renderValues(map, values, depth = 0) {
  const out = {}
  for (const [key, value] of Object.entries(map || {})) {
    out[key] = typeof value === 'string' && depth < 5 ? renderText(value, Object.assign({}, values, out)) : value
  }
  return out
}

// ------------------------------------------------------------------- execution
function executeBlock(source, args, label) {
  const sandbox = {
    require: (name) => {
      if (name === 'nuclei/http') return makeHttpModule()
      throw new Error(`module "${name}" is not provided by the shim (only nuclei/http)`)
    },
    btoa: (value) => Buffer.from(String(value), 'binary').toString('base64'),
    atob: (value) => Buffer.from(String(value), 'base64').toString('binary'),
    console
  }
  const context = vm.createContext(sandbox)
  vm.runInContext('var globalThis = this;', context)
  for (const [key, value] of Object.entries(args)) {
    if (!/^[A-Za-z_$][A-Za-z0-9_$]*$/.test(key)) throw new Error(`invalid arg name "${key}"`)
    vm.runInContext(`var ${key} = ${JSON.stringify(value)};`, context)
  }

  try {
    const value = vm.runInContext(source, context, { timeout: 600000, filename: `${label}.js` })
    return { ok: true, value }
  } catch (err) {
    return { ok: false, error: err }
  }
}

// goja's ToBoolean: strings are true unless empty
function truthy(value) {
  if (value === undefined || value === null) return false
  if (value === 0 || value === '' || value === false) return false
  return true
}

// --------------------------------------------------------------------- matchers
const SUPPORTED_DSL = /^(?:[\w\s().,'"=!&|<>+\-*/[\]%:]*|contains\(.*\)|to_lower\(.*\)|len\(.*\)|regex\(.*\))$/s

function translateDsl(expression) {
  let js = String(expression).trim()
  js = js.replace(/\bsuccess\b/g, '__success')
  js = js.replace(/\bresponse\b/g, '__response')
  js = js.replace(/\bhost\b/g, '__host')
  js = js.replace(/\bmatched\b/g, '__matched')
  js = js.replace(/\bcontains\s*\(/g, '__contains(')
  js = js.replace(/\bto_lower\s*\(/g, '__toLower(')
  js = js.replace(/\blen\s*\(/g, '__len(')
  js = js.replace(/(?<![=!<>])==(?!=)/g, '===')
  js = js.replace(/!=(?!=)/g, '!==')
  js = js.replace(/'(?:[^'\\]|\\.)*'/g, (literal) => JSON.stringify(literal.slice(1, -1)))
  return js
}

function evaluateMatcher(matcher, data, oob) {
  const part = matcher.part || 'response'
  const negative = matcher.negative === true
  const condition = matcher['condition'] || (matcher.words && matcher.words.length > 1 ? 'or' : 'and')

  if (part === 'interactsh_protocol') {
    // Not evaluable offline: the lab listener stands in for the interactsh
    // correlation server, so a recorded callback satisfies the matcher.
    if (!oob.checked) return { matched: null, detail: 'interactsh_protocol requires real nuclei + interactsh (use --oob-log)' }
    const wanted = (matcher.words || []).map((w) => String(w).toLowerCase())
    const protocols = oob.hits.map(() => 'tcp')
    const hit = wanted.length === 0 ? oob.hits.length > 0 : wanted.some((word) => protocols.includes(word) || word === 'http' || word === 'dns')
    const result = hit && oob.hits.length > 0
    return { matched: negative ? !result : result, detail: `lab OOB listener recorded ${oob.hits.length} callback(s)` }
  }

  if (part !== 'response' && part !== 'host' && part !== 'matched') {
    return { matched: null, detail: `matcher part "${part}" is not implemented by the shim` }
  }

  const subject = String(data[part] ?? '')

  if (matcher.type === 'word') {
    const words = matcher.words || []
    const found = words.map((word) => subject.includes(String(word)))
    const hit = condition === 'and' ? found.every(Boolean) : found.some(Boolean)
    const result = negative ? !hit : hit
    return { matched: result, detail: `word ${condition} [${words.join(', ')}] on ${part} (${subject.length}B)` }
  }

  if (matcher.type === 'regex') {
    const patterns = matcher.regex || matcher.regexes || []
    const found = patterns.map((pattern) => new RegExp(pattern, matcher['case-insensitive'] ? 'i' : '').test(subject))
    const hit = condition === 'and' ? found.every(Boolean) : found.some(Boolean)
    const result = negative ? !hit : hit
    return { matched: result, detail: `regex ${condition} on ${part}` }
  }

  if (matcher.type === 'dsl') {
    const results = []
    for (const expression of matcher.dsl || []) {
      if (!SUPPORTED_DSL.test(expression)) {
        return { matched: null, detail: `dsl expression not supported by the shim: ${expression}` }
      }
      const js = translateDsl(expression)
      const fn = new Function('__response', '__host', '__matched', '__success', '__contains', '__toLower', '__len',
        `return (${js});`)
      results.push(!!fn(data.response, data.host, data.matched, data.success,
        (haystack, needle) => String(haystack).includes(String(needle)),
        (value) => String(value).toLowerCase(),
        (value) => String(value).length))
    }
    const hit = condition === 'and' ? results.every(Boolean) : results.some(Boolean)
    const result = negative ? !hit : hit
    return { matched: result, detail: `dsl ${condition} [${(matcher.dsl || []).join('; ')}]` }
  }

  return { matched: null, detail: `matcher type "${matcher.type}" is not implemented by the shim` }
}

// ------------------------------------------------------------------------ main
function main() {
  const template = YAML.parse(fs.readFileSync(opts.template, 'utf8'))
  const request = (template.javascript || [])[0]
  if (!request) throw new Error(`${opts.template} has no javascript block`)

  const started = Date.now()
  say(`[shim] template ${template.id} (${template.info?.severity || 'unknown'})`)
  say(`[shim] target   ${opts.target}`)

  const std = standardVariables(opts.target)
  const templateVars = renderValues(template.variables || {}, std)
  const values = Object.assign({}, templateVars, std, opts.vars)

  const args = {}
  for (const [key, value] of Object.entries(request.args || {})) {
    args[key] = typeof value === 'string' ? renderText(value, values) : value
  }
  for (const [key, value] of Object.entries(opts.vars)) {
    if (!(key in args)) args[key] = value
  }
  say(`[shim] args     ${JSON.stringify(args)}`)

  let oob = { checked: false, hits: [], before: 0 }
  if (opts.oobLog) {
    oob.before = fs.existsSync(opts.oobLog) ? fs.readFileSync(opts.oobLog, 'utf8').split('\n').filter(Boolean).length : 0
  }

  if (request['pre-condition'] && opts.precondition) {
    const pre = executeBlock(request['pre-condition'], args, `${template.id}-precondition`)
    if (!pre.ok) {
      problem(`[shim] pre-condition error -> ${pre.error.message}`)
      return EXIT_ERROR
    }
    const satisfied = truthy(pre.value && pre.value.export ? pre.value.export() : pre.value)
    say(`[shim] pre-condition -> ${satisfied}`)
    if (!satisfied) {
      say('[shim] VERDICT  not matched (pre-condition false, request not sent)')
      return EXIT_NOT_MATCHED
    }
  }

  const executed = executeBlock(request.code, args, `${template.id}-code`)
  if (!executed.ok) {
    problem(`[shim] script error -> ${executed.error.message}`)
    return EXIT_ERROR
  }
  const response = executed.value
  const success = truthy(response)
  say(`[shim] success  ${success}`)

  // --print-response is an explicit request for the data, so it prints even
  // with --quiet (the test suite relies on it).
  if (opts.printResponse) console.log(`[shim] response ${String(response)}`)

  if (opts.oobLog) {
    oob.checked = true
    const lines = fs.existsSync(opts.oobLog) ? fs.readFileSync(opts.oobLog, 'utf8').split('\n').filter(Boolean) : []
    oob.hits = lines.slice(oob.before)
    say(`[shim] oob      ${oob.hits.length} new callback(s)${oob.hits.length ? ': ' + oob.hits.join(' | ') : ''}`)
  }

  const data = { response: String(response), success, host: std.Hostname, matched: std.Hostname }
  const matchers = request.matchers || []
  const matchersCondition = request['matchers-condition'] || 'or'
  const verdicts = []
  for (const matcher of matchers) {
    const evaluated = evaluateMatcher(matcher, data, oob)
    verdicts.push(evaluated)
    const state = evaluated.matched === null ? 'SKIP' : evaluated.matched ? 'HIT ' : 'miss'
    say(`[shim] matcher  ${state} ${evaluated.detail}`)
  }

  const evaluable = verdicts.filter((v) => v.matched !== null)
  const matched = matchersCondition === 'and'
    ? evaluable.length === verdicts.length && verdicts.every((v) => v.matched === true)
    : verdicts.some((v) => v.matched === true)

  const skipped = verdicts.filter((v) => v.matched === null).length
  if (skipped > 0) {
    say(`[shim] note     ${skipped} matcher(s) not evaluable by the shim - see SKIP above`)
  }
  say(`[shim] elapsed  ${((Date.now() - started) / 1000).toFixed(1)}s`)
  say(`[shim] VERDICT  ${matched ? 'matched' : 'not matched'}`)
  return matched ? EXIT_MATCHED : EXIT_NOT_MATCHED
}

try {
  process.exit(main())
} catch (err) {
  problem(`[shim] error -> ${err && err.message ? err.message : err}`)
  process.exit(EXIT_ERROR)
}
