/** Resolve one explicitly reviewed occurrence; never widen its scope. */
export function explicitOccurrence(change, sourceText, validOffsets) {
  if (change.startOffset === undefined && change.endOffset === undefined) return null
  const { startOffset: start, endOffset: end, expected } = change
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 ||
      end <= start || end > sourceText.length || end - start !== expected.length ||
      sourceText.slice(start, end) !== expected || !validOffsets.includes(start)) {
    throw new Error(`Invalid reviewed occurrence ${change.book} ${change.chapter}:${change.verse}`)
  }
  return start
}
