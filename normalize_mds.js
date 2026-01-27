#!/usr/bin/env node
/**
 * Normalize .md filenames recursively under each given root.
 * Usage: node normalize_mds.js /workspace/jobs/1_rico [/another/root]
 */
const fs = require('fs');
const path = require('path');

const roots = process.argv.slice(2);
if (!roots.length) {
  console.error('Usage: node normalize_mds.js <root> [<root> ...]');
  process.exit(1);
}

function normalizeName(filename) {
  const lower = filename.toLowerCase();
  const pos = lower.lastIndexOf('.md');
  if (pos === -1) return filename;
  const base = filename.slice(0, pos);
  const cleaned = base.replace(/[ \t\n\r\u000b\u000c\u200b\ufeff]+$/g, '');
  return `${cleaned}.md`;
}

function uniquePath(target) {
  if (!fs.existsSync(target)) return target;
  const dir = path.dirname(target);
  const base = path.basename(target, '.md');
  let counter = 1;
  while (true) {
    const candidate = path.join(dir, `${base}-${counter}.md`);
    if (!fs.existsSync(candidate)) return candidate;
    counter += 1;
  }
}

function walk(root) {
  const stack = [root];
  const files = [];
  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else files.push(full);
    }
  }
  return files;
}

let renamed = 0;

for (const root of roots) {
  if (!fs.existsSync(root)) {
    console.warn(`Skip missing root: ${root}`);
    continue;
  }
  for (const file of walk(root)) {
    const dir = path.dirname(file);
    const name = path.basename(file);
    const normalized = normalizeName(name);
    if (normalized === name) continue;
    let target = path.join(dir, normalized);
    if (fs.existsSync(target)) target = uniquePath(target);
    console.log(`Rename: ${file} -> ${target}`);
    fs.renameSync(file, target);
    renamed += 1;
  }
}

console.log(`Completed: ${renamed} file(s) renamed`);
