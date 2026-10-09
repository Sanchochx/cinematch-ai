import { render, screen } from '@testing-library/react';
import App from '../src/App';

describe('App', () => {
  it('carga el chat bajo demanda y renderiza el título principal', async () => {
    render(<App />);
    expect(
      await screen.findByRole('heading', { level: 1, name: 'CineMatch AI' }),
    ).toBeInTheDocument();
    expect(screen.getAllByRole('main')).toHaveLength(1);
  });
});
