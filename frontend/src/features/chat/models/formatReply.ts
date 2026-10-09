export type ReplyBlock =
  { kind: 'paragraph'; lines: string[] } | { kind: 'unordered' | 'ordered'; items: string[] };

const UNORDERED_ITEM = /^\s*[-*•]\s+(.*\S)\s*$/;
const ORDERED_ITEM = /^\s*\d+[.)]\s+(.*\S)\s*$/;

/**
 * Convierte el texto plano del asistente en bloques (párrafos y listas simples).
 * Devuelve solo strings: el HTML crudo nunca se interpreta, React lo escapa al renderizar.
 */
export function parseReply(text: string): ReplyBlock[] {
  const blocks: ReplyBlock[] = [];

  const append = (kind: ReplyBlock['kind'], line: string): void => {
    const last = blocks.at(-1);
    if (last?.kind === kind) {
      if (last.kind === 'paragraph') last.lines.push(line);
      else last.items.push(line);
      return;
    }
    blocks.push(kind === 'paragraph' ? { kind, lines: [line] } : { kind, items: [line] });
  };

  let previousBlank = true;
  for (const raw of text.split(/\r?\n/)) {
    if (raw.trim() === '') {
      previousBlank = true;
      continue;
    }
    const unordered = UNORDERED_ITEM.exec(raw);
    const ordered = ORDERED_ITEM.exec(raw);
    if (unordered?.[1] !== undefined) append('unordered', unordered[1]);
    else if (ordered?.[1] !== undefined) append('ordered', ordered[1]);
    else if (previousBlank || blocks.at(-1)?.kind !== 'paragraph') {
      blocks.push({ kind: 'paragraph', lines: [raw.trim()] });
    } else append('paragraph', raw.trim());
    previousBlank = false;
  }
  return blocks;
}
