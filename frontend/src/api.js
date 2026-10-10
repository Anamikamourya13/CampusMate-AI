/**
 * CampusMate AI - API Client
 * Clean HTTP client for interacting with the backend endpoints.
 */

export async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    if (!res.ok) throw new Error(`Health check failed (${res.status})`);
    return await res.json();
  } catch (err) {
    console.error('API Health Check Error:', err);
    return { status: 'error', error: err.message };
  }
}

export async function analyzeNotice({ text, file, language }) {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  }
  if (text) {
    formData.append('text', text);
  }
  formData.append('language', language || 'English');

  const res = await fetch('/api/notices/analyze', {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to analyze notice');
  }
  return data;
}

export async function askNoticeQuestion({ noticeText, question, language }) {
  const res = await fetch('/api/notices/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      notice_text: noticeText,
      question: question,
      language: language || 'English',
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to answer question');
  }
  return data;
}
