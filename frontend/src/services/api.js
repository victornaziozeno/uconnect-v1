const API_URL = "http://localhost:8000";

// Gerenciamento de token
const getToken = () => localStorage.getItem("access_token");
const setToken = (token) => localStorage.setItem("access_token", token);
const removeToken = () => localStorage.removeItem("access_token");

// Headers padrão com autenticação
const getHeaders = (includeAuth = true) => {
  const headers = {
    "Content-Type": "application/json",
  };
  
  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  
  return headers;
};

// Tratamento de erros
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Erro HTTP ${response.status}`);
  }
  return response.json();
};

// ==================== AUTENTICAÇÃO ====================

export const login = async (registration, password) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: getHeaders(false),
    body: JSON.stringify({
      registration: registration.trim(),
      password: password.trim(),
    }),
  });
  
  const data = await handleResponse(response);
  setToken(data.access_token);
  return data;
};

export const logout = async () => {
  try {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      headers: getHeaders(),
    });
  } finally {
    removeToken();
  }
};

export const validateSession = async () => {
  try {
    const response = await fetch(`${API_URL}/auth/validate`, {
      method: "GET",
      headers: getHeaders(),
    });
    return await handleResponse(response);
  } catch (error) {
    removeToken();
    throw error;
  }
};

// ==================== USUÁRIOS ====================

export const getCurrentUser = async () => {
  const response = await fetch(`${API_URL}/users/me`, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const updateProfile = async (userData) => {
  const response = await fetch(`${API_URL}/users/me`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
};

// ==================== EVENTOS ====================

// Converter formato frontend -> backend
const eventToBackend = (event) => {
  // Separar hora se existir
  let timestamp;
  if (event.hora && event.hora.includes(":")) {
    const horaInicio = event.hora.split(" - ")[0] || event.hora;
    timestamp = `${event.date}T${horaInicio}:00`;
  } else {
    timestamp = `${event.date}T00:00:00`;
  }
  
  return {
    title: event.title || event.titulo,
    description: event.descricao || "",
    timestamp: timestamp,
    academicGroupId: event.local || null,
    // Nota: eventType não existe no modelo, mas está no schema
    // Se o backend aceitar, envie. Caso contrário, remova esta linha.
  };
};

// Converter formato backend -> frontend
const eventFromBackend = (event) => {
  const date = event.timestamp.split("T")[0];
  const time = event.timestamp.split("T")[1]?.substring(0, 5) || "";
  
  return {
    id: event.id,
    title: event.title,
    date: date,
    hora: time || "",
    descricao: event.description || "",
    local: event.academicGroupId || "",
    //tipo: "Evento Geral", // Valor padrão já que não existe no backend
  };
};

export const getEvents = async () => {
  const response = await fetch(`${API_URL}/events`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }, // Público, sem auth
  });
  
  const data = await handleResponse(response);
  return data.map(eventFromBackend);
};

export const getEvent = async (eventId) => {
  const response = await fetch(`${API_URL}/events/${eventId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const createEvent = async (event) => {
  const response = await fetch(`${API_URL}/events`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(eventToBackend(event)),
  });
  
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const updateEvent = async (eventId, event) => {
  const response = await fetch(`${API_URL}/events/${eventId}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(eventToBackend(event)),
  });
  
  const data = await handleResponse(response);
  return eventFromBackend(data);
};

export const deleteEvent = async (eventId) => {
  const response = await fetch(`${API_URL}/events/${eventId}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`Erro ao deletar evento: ${response.status}`);
  }
  
  return { success: true };
};

// ==================== UTILITÁRIOS ====================

export const isAuthenticated = () => {
  return !!getToken();
};

export { getToken, setToken, removeToken };