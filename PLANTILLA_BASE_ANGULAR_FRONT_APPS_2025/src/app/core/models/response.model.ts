/**
 * Respuesta genérica de la API
 * Usado para normalizar respuestas de servicios
 */
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: string[];
}

/**
 * Respuesta de autenticación
 */
export interface AuthResponse {
  authenticated: boolean;
  user?: {
    username: string;
    nombre: string;
    email: string;
  };
  message?: string;
}

/**
 * Respuesta paginada
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
