// 认证相关类型定义

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email?: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  bio?: string;
  avatar?: string;
  avatar_url?: string;
  date_joined: string;
  last_login: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  csrf_token?: string;
  message: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}
