let csrf = '';

export function setCsrf(value) {
  csrf = value;
}

export async function api(path, options = {}) {
  const urlWithDebug = `/api${path}${path.includes('?') ? '&' : '?'}XDEBUG_SESSION=REACT_DEBUG`;

  const response = await fetch(urlWithDebug, {
    credentials: 'same-origin',
    ...options,
    headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf, ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(data.message || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return data;
}
