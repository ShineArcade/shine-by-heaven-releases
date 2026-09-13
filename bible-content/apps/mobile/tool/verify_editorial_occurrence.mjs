import assert from 'node:assert/strict'
import { explicitOccurrence } from './editorial_occurrence.mjs'
const source = 'word and word'
const c = { book: 'MAT', chapter: 1, verse: 1, expected: 'word', startOffset: 9, endOffset: 13 }
assert.equal(explicitOccurrence(c, source, [0,9]), 9)
assert.equal(explicitOccurrence({expected:'word'}, source, [0,9]), null)
for (const bad of [{startOffset:-1}, {endOffset:12}, {startOffset:1,endOffset:5}, {endOffset:99}, {startOffset:9.5}, {endOffset:undefined}]) {
  assert.throws(() => explicitOccurrence({...c,...bad},source,[0,9]))
}
assert.throws(() => explicitOccurrence(c,source,[0]))
console.log('PASS: exact repeated-word occurrence, legacy route, stale span and word-boundary rejection')
