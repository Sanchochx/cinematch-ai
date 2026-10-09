import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from '../../axe';
import { ChatComposer } from '../../../src/features/chat/components/ChatComposer';
import { EmptyState } from '../../../src/features/chat/components/EmptyState';
import { ErrorBanner } from '../../../src/features/chat/components/ErrorBanner';
import { MessageBubble } from '../../../src/features/chat/components/MessageBubble';
import { MessageList } from '../../../src/features/chat/components/MessageList';
import { TypingIndicator } from '../../../src/features/chat/components/TypingIndicator';
import { ChatError } from '../../../src/features/chat/models/chat';
import type { ChatMessage } from '../../../src/features/chat/models/chat';

const messages: ChatMessage[] = [
  { id: '1', role: 'user', content: 'Quiero ciencia ficción', status: 'sent' },
  { id: '2', role: 'assistant', content: 'Te sugiero:\n- Arrival\n- Dune', status: 'sent' },
];

describe('EmptyState', () => {
  it('muestra 3 sugerencias y notifica la elegida', async () => {
    const onSelect = vi.fn();
    render(<EmptyState onSelect={onSelect} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(3);
    await userEvent.click(buttons[1]!);
    expect(onSelect).toHaveBeenCalledWith(buttons[1]!.textContent);
  });
});

describe('MessageBubble', () => {
  it('renderiza mensajes de usuario y asistente (listas incluidas)', () => {
    render(
      <ul>
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </ul>,
    );
    expect(screen.getByText('Quiero ciencia ficción')).toBeInTheDocument();
    expect(screen.getAllByRole('listitem').length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText('Arrival')).toBeInTheDocument();
  });

  it('escapa el HTML de la respuesta: se muestra como texto', () => {
    const { container } = render(
      <ul>
        <MessageBubble
          message={{
            id: '3',
            role: 'assistant',
            content: '<img src=x onerror=alert(1)><script>boom()</script>',
          }}
        />
      </ul>,
    );
    expect(container.querySelector('img, script')).toBeNull();
    expect(screen.getByText(/<img src=x onerror=alert\(1\)>/)).toBeInTheDocument();
  });

  it('marca los mensajes no enviados', () => {
    render(
      <ul>
        <MessageBubble message={{ id: '4', role: 'user', content: 'hola', status: 'error' }} />
      </ul>,
    );
    expect(screen.getByText('No se pudo enviar')).toBeInTheDocument();
  });
});

describe('MessageList', () => {
  it('es una región log con aria-live y muestra el indicador de escritura', () => {
    render(<MessageList messages={messages} isLoading />);
    const log = screen.getByRole('log');
    expect(log).toHaveAttribute('aria-live', 'polite');
    expect(screen.getByText('El asistente está escribiendo')).toBeInTheDocument();
  });
});

describe('TypingIndicator', () => {
  it('anuncia el estado de carga', () => {
    render(
      <ul>
        <TypingIndicator />
      </ul>,
    );
    expect(screen.getByText('El asistente está escribiendo')).toBeInTheDocument();
  });
});

describe('ErrorBanner', () => {
  it('muestra el mensaje en español y permite reintentar', async () => {
    const onRetry = vi.fn();
    render(<ErrorBanner error={new ChatError('timeout')} onRetry={onRetry} />);
    expect(screen.getByRole('alert')).toHaveTextContent('La respuesta ha tardado demasiado');
    await userEvent.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(onRetry).toHaveBeenCalledOnce();
  });
});

describe('ChatComposer', () => {
  const setup = (isLoading = false) => {
    const onSend = vi.fn().mockResolvedValue(undefined);
    render(<ChatComposer onSend={onSend} isLoading={isLoading} />);
    return { onSend, input: screen.getByLabelText('Tu mensaje') };
  };

  it('Enter envía, limpia el campo y devuelve el foco al textarea', async () => {
    const { onSend, input } = setup();
    await userEvent.type(input, 'hola{Enter}');
    expect(onSend).toHaveBeenCalledWith('hola');
    expect(input).toHaveValue('');
    expect(input).toHaveFocus();
  });

  it('Shift+Enter inserta salto de línea y no envía', async () => {
    const { onSend, input } = setup();
    await userEvent.type(input, 'a{Shift>}{Enter}{/Shift}b');
    expect(onSend).not.toHaveBeenCalled();
    expect(input).toHaveValue('a\nb');
  });

  it('no envía mensajes vacíos', async () => {
    const { onSend, input } = setup();
    expect(screen.getByRole('button', { name: 'Enviar' })).toBeDisabled();
    await userEvent.type(input, '   {Enter}');
    expect(onSend).not.toHaveBeenCalled();
  });

  it('el botón envía y mantiene el foco en el textarea', async () => {
    const { onSend, input } = setup();
    await userEvent.type(input, 'hola');
    await userEvent.click(screen.getByRole('button', { name: 'Enviar' }));
    expect(onSend).toHaveBeenCalledWith('hola');
    expect(input).toHaveFocus();
  });

  it('con isLoading bloquea el envío sin perder el texto', async () => {
    const { onSend, input } = setup(true);
    await userEvent.type(input, 'hola{Enter}');
    expect(onSend).not.toHaveBeenCalled();
    expect(input).toHaveValue('hola');
    expect(screen.getByRole('button', { name: 'Enviar' })).toBeDisabled();
  });

  it('>2000 caracteres: error asociado por aria-describedby y sin envío', async () => {
    const { onSend, input } = setup();
    await userEvent.click(input);
    await userEvent.paste('a'.repeat(2001));
    await userEvent.keyboard('{Enter}');
    expect(onSend).not.toHaveBeenCalled();
    expect(input).toHaveAttribute('aria-invalid', 'true');
    const error = screen.getByText(/no puede superar los 2000/);
    expect(input.getAttribute('aria-describedby')).toContain(error.id);
  });
});

describe('accesibilidad (axe)', () => {
  it('estado vacío', async () => {
    const { container } = render(<EmptyState onSelect={() => undefined} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('con mensajes y compositor', async () => {
    const { container } = render(
      <>
        <MessageList messages={messages} isLoading />
        <ChatComposer onSend={async () => undefined} isLoading={false} />
      </>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it('con error', async () => {
    const { container } = render(
      <ErrorBanner error={new ChatError('network')} onRetry={() => undefined} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
