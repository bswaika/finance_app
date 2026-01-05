const BASE_URL = window.API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const message = data?.detail || res.statusText;
    throw new Error(message);
  }

  return data;
}

export function login(username, password) {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function register(payload) {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchMe() {
  return request("/api/auth/me");
}

export function fetchAccounts() {
  return request("/api/accounts");
}

export function createAccount(payload) {
  return request("/api/accounts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchTransactions(params = {}) {
  const query = new URLSearchParams(params);
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request(`/api/transactions${suffix}`);
}

export function createTransaction(payload) {
  return request("/api/transactions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchCategories() {
  return request("/api/categories");
}

export function createCategory(payload) {
  return request("/api/categories", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

