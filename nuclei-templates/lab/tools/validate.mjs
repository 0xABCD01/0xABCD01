#!/usr/bin/env node
// Offline validation for the templates in this directory, standing in for
// `nuclei -validate` (unavailable here: no Go toolchain, release downloads
// blocked):
//
//   1. YAML parses
//   2. the document satisfies the nuclei JSON schema (vendored copy)
//   3. every init / pre-condition / code block is syntactically valid JS
//
// Usage: node validate.mjs ../../CVE-2026-94545.yaml [...]
//        node validate.mjs --all
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)
const YAML = require('yaml')
const Ajv = require('ajv/dist/2020')  // the nuclei schema declares draft 2020-12
const addFormats = require('ajv-formats')

const HERE = path.dirname(fileURLToPath(import.meta.url))
const TEMPLATE_DIR = path.resolve(HERE, '..', '..')

const args = process.argv.slice(2)
let files = args.filter((a) => !a.startsWith('--'))
if (args.includes('--all') || files.length === 0) {
  files = fs.readdirSync(TEMPLATE_DIR)
    .filter((name) => name.endsWith('.yaml') || name.endsWith('.yml'))
    .map((name) => path.join(TEMPLATE_DIR, name))
}

const schemaPath = path.join(HERE, 'nuclei-jsonschema.json')
let validate = null
if (fs.existsSync(schemaPath)) {
  const ajv = new Ajv({ allErrors: true, strict: false, allowUnionTypes: true })
  addFormats(ajv)
  validate = ajv.compile(JSON.parse(fs.readFileSync(schemaPath, 'utf8')))
} else {
  console.log(`note: ${schemaPath} missing - skipping the schema check (fetch it with:`)
  console.log('      curl -o tools/nuclei-jsonschema.json \\')
  console.log('        https://raw.githubusercontent.com/projectdiscovery/nuclei/main/nuclei-jsonschema.json)')
}

let failures = 0
const fail = (file, message) => {
  failures += 1
  console.log(`  FAIL ${message}`)
}

for (const file of files) {
  console.log(`\n${path.basename(file)}`)
  let doc
  try {
    doc = YAML.parse(fs.readFileSync(file, 'utf8'))
    console.log('  yaml   ok')
  } catch (err) {
    fail(file, `yaml: ${err.message}`)
    continue
  }

  if (validate) {
    if (validate(doc)) {
      console.log('  schema ok')
    } else {
      for (const error of validate.errors) {
        fail(file, `schema: ${error.instancePath} ${error.message}`)
      }
    }
  }

  for (const block of doc.javascript || []) {
    for (const key of ['init', 'pre-condition', 'code']) {
      const source = block[key]
      if (typeof source !== 'string' || source.length === 0) continue
      try {
        // eslint-disable-next-line no-new-func
        new Function(source)
        console.log(`  js     ${key} ok (${source.split('\n').length} lines)`)
      } catch (err) {
        fail(file, `js ${key}: ${err.message}`)
      }
    }
  }

  const ids = [doc.id, ...(doc.javascript || []).map(() => '')]
  const argsList = (doc.javascript || []).map((b) => Object.keys(b.args || {}).join(', ')).filter(Boolean)
  if (argsList.length) console.log(`  args   ${argsList.join(' | ')}`)
  const matchers = (doc.javascript || []).flatMap((b) => (b.matchers || []).map((m) => m.type))
  if (matchers.length) console.log(`  match  ${matchers.join(', ')}`)
  if (!ids[0]) fail(file, 'missing template id')
}

console.log(`\n${failures === 0 ? 'VALIDATION PASSED' : `VALIDATION FAILED (${failures})`}`)
process.exit(failures === 0 ? 0 : 1)
