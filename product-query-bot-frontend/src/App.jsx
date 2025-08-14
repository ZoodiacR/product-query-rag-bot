import React, { useState } from 'react';
// Importaciones de Material-UI
import {
  Box,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Container,
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
// Importar nuevos colores base: teal, blue, grey, red
import { teal, blue, grey, red } from '@mui/material/colors';

// Importaciones de iconos de Material-UI
import SendIcon from '@mui/icons-material/Send';
import InfoIcon from '@mui/icons-material/Info';
import RefreshIcon from '@mui/icons-material/Refresh';

// Definir el tema personalizado de Material-UI con la nueva paleta
const theme = createTheme({
  palette: {
    primary: { // Colores primarios (aguamarina para botones principales, acentos)
      main: teal[600],
      light: teal[400],
      dark: teal[800],
      contrastText: '#fff',
    },
    secondary: { // Colores secundarios (azul para títulos, degradados)
      main: blue[800],
      light: blue[600],
      dark: blue[900],
      contrastText: '#fff',
    },
    background: {
      // Nuevo degradado de fondo para la página (azul claro a aguamarina claro)
      default: `linear-gradient(to bottom right, ${blue[50]}, ${teal[100]})`,
      paper: '#fff', // Fondo para la tarjeta principal (blanco puro)
    },
    text: {
      primary: grey[800], // Color de texto principal
      secondary: grey[700], // Color de texto secundario (ej. labels de TextField)
    },
    error: { // Colores para mensajes de error
      main: red[700],
      light: red[50],
      contrastText: red[700], // Para que el texto sea visible en fondo light
    },
    // Añadir colores personalizados para fondos de elementos internos
    custom: {
      tealLightBg: teal[50], // Para el fondo de la caja de texto
      tealBorder: teal[300], // Para los bordes
      tealResponseBg: teal[100], // Para el fondo de la respuesta
    }
  },
  typography: {
    fontFamily: ['Inter', 'sans-serif'].join(','), // Usa la fuente Inter
    h1: {
      fontWeight: 700, // Títulos en negrita
      color: blue[800], // Color de título (azul oscuro)
    },
    h2: {
      fontWeight: 600,
      color: teal[800], // Color de subtítulos (aguamarina oscuro)
    },
  },
  components: {
    // Estilos personalizados para los componentes de MUI
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8, // Bordes redondeados
          boxShadow: '0px 3px 6px rgba(0, 0, 0, 0.15)', // Sombra sutil
          transition: 'transform 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)', // Efecto hover
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
            backgroundColor: teal[50], // Fondo aguamarina claro
            '& fieldset': { // Borde del TextField
              borderColor: teal[300],
            },
            '&:hover fieldset': {
              borderColor: teal[400],
            },
            '&.Mui-focused fieldset': {
              borderColor: teal[500],
            },
          },
        },
      },
    },
    MuiPaper: { // Utilizaremos Paper para la tarjeta principal del chat
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.15)', // Sombra más pronunciada
          border: `1px solid ${teal[200]}`, // Borde de la tarjeta
          backgroundColor: '#fff',
        }
      }
    },
    MuiAlert: { // Estilo para los mensajes de error
      styleOverrides: {
        root: {
          borderRadius: '8px',
          backgroundColor: red[50],
          border: `1px solid ${red[200]}`,
          color: red[700],
          display: 'flex', // Para alinear icono y texto
          alignItems: 'center',
        },
      }
    },
    MuiOutlinedInput: {
        styleOverrides: {
            input: {
                color: grey[800], // Color del texto del input
                '&::placeholder': { // Color del placeholder
                    color: grey[500],
                    opacity: 1, // Asegura que el placeholder se vea
                },
            },
        },
    },
  },
});

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse('');

    if (!query.trim()) {
      setError('Por favor, introduce una pregunta.');
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: 'frontend_user', query: query }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      console.error("Error al consultar el bot:", err);
      setError(`Error al conectar con el servicio: ${err.message}. Asegúrate de que el backend esté corriendo y los datos indexados.`);
    } finally {
      setLoading(false);
    }
  };

  const handleIndexData = async () => {
    setLoading(true);
    setError(null);
    setResponse('');
    try {
      const res = await fetch(`${API_BASE_URL}/index`, {
        method: 'POST',
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      alert(data.message); // Usar alert para mensajes de confirmación simple, o modal si fuera más complejo
    } catch (err) {
      console.error("Error al indexar datos:", err);
      setError(`Error al indexar datos: ${err.message}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    // ThemeProvider envuelve toda la aplicación para que los componentes usen el tema
    <ThemeProvider theme={theme}>
      {/* Box principal para el fondo de pantalla y centrado */}
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 2,
          background: theme.palette.background.default, // Usa el degradado definido en el tema
          fontFamily: theme.typography.fontFamily,
        }}
      >
        {/* Contenedor para el chat (simula la tarjeta rectangular) */}
        <Container
          maxWidth="sm" // Limita el ancho, similar a max-w-2xl
          sx={{
            backgroundColor: theme.palette.background.paper, // Fondo blanco
            borderRadius: '12px', // Bordes redondeados
            boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.15)', // Sombra
            border: `1px solid ${theme.palette.custom.tealBorder}`, // Borde sutil (aguamarina)
            padding: { xs: 3, md: 4 },
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
          }}
        >
          {/* Título */}
          <Typography variant="h1" align="center" sx={{ color: theme.palette.secondary.main }}>
            Product Query Bot
          </Typography>

          {/* Formulario de consulta */}
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Tu Pregunta sobre Productos:"
              multiline
              rows={4}
              fullWidth
              variant="outlined"
              placeholder="Ej: ¿Cuáles son las características principales de la Cafetera Inteligente?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: theme.palette.custom.tealLightBg, // Fondo aguamarina claro para el campo
                },
                '& .MuiInputLabel-root': { // Estilo para el label
                    color: theme.palette.text.secondary,
                },
              }}
            />

            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                disabled={loading}
                sx={{ flexGrow: 1, paddingY: '12px' }}
              >
                {loading ? 'Consultando...' : 'Enviar Pregunta'}
              </Button>
              <Button
                type="button"
                variant="outlined" // outlined para el botón secundario
                startIcon={<RefreshIcon />}
                onClick={handleIndexData}
                disabled={loading}
                sx={{
                  flexGrow: 1,
                  paddingY: '12px',
                  borderColor: theme.palette.primary.main, // Borde aguamarina
                  color: theme.palette.primary.main, // Texto aguamarina
                  '&:hover': {
                    backgroundColor: theme.palette.primary.light, // Fondo aguamarina claro al hover
                    borderColor: theme.palette.primary.main, // Mantener borde aguamarina
                  },
                }}
              >
                Indexar Datos
              </Button>
            </Box>
          </Box>

          {/* Mensajes de error */}
          {error && (
            <Alert severity="error" icon={<InfoIcon />} sx={{ marginTop: 3 }}>
              {error}
            </Alert>
          )}

          {/* Área de respuesta */}
          {response && (
            <Box
              sx={{
                marginTop: 3,
                padding: 3,
                backgroundColor: theme.palette.custom.tealResponseBg, // Fondo aguamarina claro
                border: `1px solid ${theme.palette.custom.tealBorder}`, // Borde aguamarina
                borderRadius: '8px',
                boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.1)', // Sombra interna
              }}
            >
              <Typography variant="h2" sx={{ color: theme.palette.primary.dark, marginBottom: 1 }}>
                Respuesta del Bot:
              </Typography>
              <Typography sx={{ color: theme.palette.text.primary, whiteSpace: 'pre-wrap' }}>
                {response}
              </Typography>
            </Box>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
