/**
 * HomeMatch Frontend — API Client
 * Thin fetch wrappers around the Django REST backend.
 */

export const BASE_URL = "http://localhost:8000";

// Token / session helpers 
export const Auth = {
  getAccess:  () => localStorage.getItem("hm_access"),
  getRefresh: () => localStorage.getItem("hm_refresh"),

  set(access, refresh) {
    localStorage.setItem("hm_access", access);
    if (refresh) localStorage.setItem("hm_refresh", refresh);
  },

  clear() {
    localStorage.removeItem("hm_access");
    localStorage.removeItem("hm_refresh");
  },

  isLoggedIn: () => !!localStorage.getItem("hm_access"),
};

// Core request
async function req(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};

  if (body) {
    headers["Content-Type"] = "application/json";
  }

  if (auth && Auth.getAccess()) {
    headers["Authorization"] = `Bearer ${Auth.getAccess()}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));

    throw Object.assign(
      new Error(err.detail || JSON.stringify(err) || "Falha na requisição"),
      { status: res.status, data: err }
    );
  }

  return res.status === 204 ? null : res.json();
}

function cleanParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== "" && v != null)
  );
}

function buildQueryString(params = {}) {
  return new URLSearchParams(cleanParams(params)).toString();
}

// Auth endpoints 
export async function login(email, password) {
  const data = await req("/api/users/login/", {
    method: "POST",
    body: { email, password },
  });

  Auth.set(data.access, data.refresh);
  return data;
}

export async function register(name, email, password, user_type = "S") {
  return req("/api/users/register/", {
    method: "POST",
    body: { name, email, password, user_type },
  });
}

export async function logout() {
  const refresh = Auth.getRefresh();

  if (refresh) {
    await req("/api/users/logout/", {
      method: "POST",
      body: { refresh },
      auth: true,
    }).catch(() => {});
  }

  Auth.clear();
}

export async function getMe() {
  return req("/api/users/me/", { auth: true });
}

export async function updateMe(data) {
  return req("/api/users/me/", {
    method: "PATCH",
    body: data,
    auth: true,
  });
}

// Properties 
export async function getProperties(params = {}) {
  const qs = buildQueryString(params);
  return req(`/api/properties/${qs ? "?" + qs : ""}`);
}

export async function getProperty(id) {
  return req(`/api/properties/${id}/`);
}

/**
 * Natural-language property search endpoint.
 *
 * This endpoint is intentionally backend-owned:
 * the frontend only forwards q + objective filters and renders the response
 * in the order returned by the backend.
 *
 * Expected endpoint:
 *   GET /api/search/properties/?q=...&city=...&type=...
 */
export async function searchProperties(params = {}) {
  const qs = buildQueryString(params);
  return req(`/api/search/properties/${qs ? "?" + qs : ""}`);
}

export async function naturalLanguageSearch(query, filters = {}) {
  return searchProperties({
    ...filters,
    q: query,
  });
}

// Favorites 
export async function getFavorites() {
  return req("/api/users/favorites/", { auth: true });
}

export async function addFavorite(property_id) {
  return req("/api/users/favorites/", {
    method: "POST",
    body: { property_id },
    auth: true,
  });
}

export async function removeFavorite(property_id) {
  return req("/api/users/favorites/", {
    method: "DELETE",
    body: { property_id },
    auth: true,
  });
}

// Reviews 
export async function getReviews(property_id) {
  return req(`/api/properties/${property_id}/reviews/`);
}

export async function createReview(property_id, rating, comment) {
  return req(`/api/properties/${property_id}/reviews/`, {
    method: "POST",
    body: { rating, comment },
    auth: true,
  });
}

// Formatting helpers
export function fmtPrice(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

export const TYPE_LABEL = {
  A: "Apartamento",
  H: "Casa",
};

export const PURPOSE_LABEL = {
  S: "Venda",
  R: "Aluguel",
  B: "Venda/Aluguel",
};