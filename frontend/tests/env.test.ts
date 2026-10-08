import { resolveApiUrl } from '../src/config/env';

describe('resolveApiUrl', () => {
  it('usa el valor por defecto si no hay variable', () => {
    expect(resolveApiUrl(undefined)).toBe('http://localhost:3000');
    expect(resolveApiUrl('  ')).toBe('http://localhost:3000');
  });

  it('respeta la variable y quita barras finales', () => {
    expect(resolveApiUrl('http://api.test:4000//')).toBe('http://api.test:4000');
  });
});
