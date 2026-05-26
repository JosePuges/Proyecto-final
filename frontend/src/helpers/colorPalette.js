/**
 * Color Palette - Dopamine Edition
 *
 * Paleta de colores vibrante para la interfaz.
 * Usa estos valores en cualquier lugar de la app que necesite colores.
 */

export const colorPalette = {
  // Primarios - Naranja vibrante (estilo portalápices)
  primary: '#FF7043',
  primaryLight: '#FFB74D',
  primaryDark: '#E64A19',

  // Accent - Magenta/Rosa intenso
  accent: '#FF1493',
  accentLight: '#FF69B4',
  accentDark: '#CC0066',

  // Estados
  success: '#00D99F',        // Verde mint vibrante
  warning: '#FFD700',        // Amarillo
  error: '#FF6B6B',          // Rojo suave

  // Backgrounds
  bgPrimary: '#FFFAF5',      // Blanco cálido (fondo principal)
  bgSecondary: '#FFF5E6',    // Crema muy clara
  bgTertiary: '#FFE8CC',     // Crema pastel

  // Texto
  textPrimary: '#2C2C2C',
  textSecondary: '#666666',
  textTertiary: '#999999',

  // Bordes
  border: '#FFE0B2',
  borderLight: '#FFF0DB',

  // Sombras (para gradientes)
  shadow: 'rgba(255, 112, 67, 0.08)',
  shadowDark: 'rgba(255, 20, 147, 0.1)',
};

/**
 * Gradientes predefinidos (cálidos como el portalápices)
 */
export const gradients = {
  header: `linear-gradient(135deg, ${colorPalette.primaryLight} 0%, ${colorPalette.primary} 50%, ${colorPalette.accent} 100%)`,
  background: `linear-gradient(135deg, ${colorPalette.bgPrimary} 0%, ${colorPalette.bgSecondary} 100%)`,
  button: `linear-gradient(135deg, ${colorPalette.primary} 0%, ${colorPalette.primaryLight} 100%)`,
  buttonHover: `linear-gradient(135deg, ${colorPalette.primaryDark} 0%, ${colorPalette.primary} 100%)`,
  accent: `linear-gradient(135deg, ${colorPalette.accent} 0%, ${colorPalette.accentLight} 100%)`,
};

/**
 * Sombras (elevation)
 */
export const shadows = {
  sm: `0 2px 8px ${colorPalette.shadow}`,
  md: `0 4px 16px ${colorPalette.shadow}`,
  lg: `0 8px 32px ${colorPalette.shadow}`,
  xl: `0 16px 48px ${colorPalette.shadowDark}`,
};

export default colorPalette;
