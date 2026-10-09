import { parseReply } from '../../../src/features/chat/models/formatReply';

describe('parseReply', () => {
  it('separa párrafos y conserva saltos de línea simples', () => {
    expect(parseReply('Hola\nmundo\n\nSegundo')).toEqual([
      { kind: 'paragraph', lines: ['Hola', 'mundo'] },
      { kind: 'paragraph', lines: ['Segundo'] },
    ]);
  });

  it('convierte listas con guion y numeradas', () => {
    expect(parseReply('Opciones:\n- Dune\n- Arrival\n\n1. Uno\n2) Dos')).toEqual([
      { kind: 'paragraph', lines: ['Opciones:'] },
      { kind: 'unordered', items: ['Dune', 'Arrival'] },
      { kind: 'ordered', items: ['Uno', 'Dos'] },
    ]);
  });

  it('devuelve [] para texto vacío y mantiene el HTML como texto', () => {
    expect(parseReply('  \n ')).toEqual([]);
    expect(parseReply('<b>x</b>')).toEqual([{ kind: 'paragraph', lines: ['<b>x</b>'] }]);
  });
});
