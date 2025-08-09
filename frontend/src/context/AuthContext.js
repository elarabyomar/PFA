import React, { createContext, useContext, useReducer, useEffect } from 'react';
import jwtDecode from 'jwt-decode';
import { login as loginService, getCurrentUser } from '../services/authService';

import { JWT_STORAGE_KEY } from '../config/api';

const AuthContext = createContext();

export { AuthContext };

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  requiresPasswordChange: false,
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        requiresPasswordChange: action.payload.requiresPasswordChange || false,
      };
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        requiresPasswordChange: false,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        requiresPasswordChange: false,
      };
    
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    
    case 'PASSWORD_CHANGED':
      return {
        ...state,
        requiresPasswordChange: false,
        user: {
          ...state.user,
          password_changed: true,
        },
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Vérifier le token au chargement
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem(JWT_STORAGE_KEY);
        if (token) {
          // Vérifier si le token n'est pas expiré
          const decoded = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp > currentTime) {
            // Token valide, récupérer les infos utilisateur
            const userInfo = await getCurrentUser();
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: {
                user: userInfo,
                token,
                requiresPasswordChange: false,
              },
            });
          } else {
            // Token expiré
            localStorage.removeItem(JWT_STORAGE_KEY);
            dispatch({ type: 'LOGIN_FAILURE' });
          }
        } else {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (error) {
        console.error('Erreur lors de l\'initialisation de l\'auth:', error);
        localStorage.removeItem(JWT_STORAGE_KEY);
        dispatch({ type: 'LOGIN_FAILURE' });
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      dispatch({ type: 'LOGIN_START' });
      
      const response = await loginService({ email, password });
      
      localStorage.setItem(JWT_STORAGE_KEY, response.access_token);
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: response.user,
          token: response.access_token,
          requiresPasswordChange: response.requires_password_change || false,
        },
      });



      return response;
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem(JWT_STORAGE_KEY);
    dispatch({ type: 'LOGOUT' });
  };

  const updateUser = (userData) => {
    dispatch({
      type: 'UPDATE_USER',
      payload: userData,
    });
  };

  const passwordChanged = () => {
    dispatch({ type: 'PASSWORD_CHANGED' });
  };

  const value = {
    ...state,
    login,
    logout,
    updateUser,
    passwordChanged,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
}; 