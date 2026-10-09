import { configureAxe } from 'vitest-axe';

// jsdom no calcula estilos reales: el contraste de color se verifica con los tokens (AA) y con Lighthouse.
export const axe = configureAxe({ rules: { 'color-contrast': { enabled: false } } });
