import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from '../../axe';
import { ChatWindow } from '../../../src/features/chat';
import { ChatError } from '../../../src/features/chat/models/chat';
import { chatService } from '../../../src/features/chat/services/chatService';

afterEach(() => vi.restoreAllMocks());

// La app real monta el chat dentro de <main>; sin él axe reportaría falsos positivos de landmarks.
const renderInMain = (): ReturnType<typeof render> =>
  render(
    <main>
      <ChatWindow />
    </main>,
  );

describe('ChatWindow', () => {
  it('muestra el estado vacío con un único h1', () => {
    render(<ChatWindow />);
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1);
    expect(screen.getAllByRole('button', { name: /pel[ií]cula|comedia|suspense/i })).toHaveLength(
      3,
    );
  });

  it('un prompt sugerido envía el mensaje y muestra la respuesta formateada', async () => {
    vi.spyOn(chatService, 'sendMessage').mockResolvedValue({ reply: 'Prueba:\n- Arrival' });
    render(<ChatWindow />);
    await userEvent.click(screen.getByRole('button', { name: /Interstellar/ }));
    expect(await screen.findByText('Arrival')).toBeInTheDocument();
    expect(screen.getByRole('log')).toBeInTheDocument();
  });

  it('muestra el indicador de escritura mientras carga', async () => {
    let resolve!: (v: { reply: string }) => void;
    vi.spyOn(chatService, 'sendMessage').mockReturnValue(new Promise((r) => (resolve = r)));
    render(<ChatWindow />);
    await userEvent.type(screen.getByLabelText('Tu mensaje'), 'hola{Enter}');
    expect(await screen.findByText('El asistente está escribiendo')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Enviar' })).toBeDisabled();
    resolve({ reply: 'listo' });
    await waitFor(() =>
      expect(screen.queryByText('El asistente está escribiendo')).not.toBeInTheDocument(),
    );
  });

  it('en error muestra el banner y Reintentar recupera la conversación', async () => {
    vi.spyOn(chatService, 'sendMessage')
      .mockRejectedValueOnce(new ChatError('unavailable'))
      .mockResolvedValueOnce({ reply: 'Ya funciona' });
    renderInMain();
    await userEvent.type(screen.getByLabelText('Tu mensaje'), 'hola{Enter}');
    expect(await screen.findByRole('alert')).toHaveTextContent('no está disponible');
    expect(await axe(document.body)).toHaveNoViolations();

    await userEvent.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(await screen.findByText('Ya funciona')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getAllByText('hola')).toHaveLength(1);
  });

  it('sin violaciones de accesibilidad en el estado vacío y con mensajes', async () => {
    vi.spyOn(chatService, 'sendMessage').mockResolvedValue({ reply: 'Hola' });
    const { container } = renderInMain();
    expect(await axe(container)).toHaveNoViolations();
    await userEvent.type(screen.getByLabelText('Tu mensaje'), 'hola{Enter}');
    await screen.findByText('Hola');
    expect(await axe(container)).toHaveNoViolations();
  });
});
