/**
 * Modelo de usuario
 * Representa la información del usuario autenticado
 */
export interface User {
  id: number;
  username: string;
  email: string;
  nombre: string;
  apellido: string;
  rol?: string;
  permisos?: string[];
}

/**
 * Información del token decodificado
 * Formato: "algo;usuario;key;bearerToken;idTarea"
 */
export interface TokenInfo {
  algo: string;
  usuario: string;
  key: string;
  bearerToken: string;
  idTarea?: string;
}
