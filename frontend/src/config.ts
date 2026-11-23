export const API = import.meta.env.PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Convierte "imagenes/perro.png" en la URL completa del servidor
export function urlArchivo(ruta: string | null | undefined): string | null {
  return ruta ? `${API}/uploads/${ruta}` : null;
}