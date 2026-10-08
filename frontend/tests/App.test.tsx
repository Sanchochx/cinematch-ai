import { render, screen } from '@testing-library/react';
import App from '../src/App';

describe('App', () => {
  it('renderiza el título principal', () => {
    render(<App />);
    expect(screen.getByRole('heading', { level: 1, name: 'CineMatch AI' })).toBeInTheDocument();
  });
});
