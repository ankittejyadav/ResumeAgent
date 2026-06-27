import { writable } from 'svelte/store';

// Backend URL: set VITE_BACKEND_URL in Vercel env vars for deployed live mode.
// Defaults to localhost for local development.
const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const state = writable({
  todos: [],
  skills: [],
  activeAgents: new Set(),
  scoreBefore: null,
  scoreAfter: null,
  missingKeywords: [],
  matchedKeywords: [],
  deliverables: {},
  log: [],
  usage: null,
  done: false,
  running: false,
});

let _es = null;
let _mockTimers = [];

function apply(evt) {
  state.update(s => {
    switch (evt.type) {
      case 'run_started':
        return { ...s, running: true, done: false, todos: [], skills: [], activeAgents: new Set(), scoreBefore: null, scoreAfter: null, missingKeywords: [], matchedKeywords: [], deliverables: {}, log: [], usage: null };

      case 'skill_loaded':
        return { ...s, skills: [...s.skills, evt.payload] };

      case 'plan':
        return { ...s, todos: evt.payload.todos };

      case 'todo_update': {
        const todos = s.todos.map(t => t.id === evt.payload.id ? { ...t, status: evt.payload.status } : t);
        return { ...s, todos };
      }

      case 'subagent_start': {
        const next = new Set(s.activeAgents);
        next.add(evt.payload.name);
        return { ...s, activeAgents: next };
      }

      case 'subagent_finish':
      case 'subagent_error': {
        const next = new Set(s.activeAgents);
        next.delete(evt.payload.name);
        const logLine = evt.type === 'subagent_error'
          ? { level: 'error', message: `${evt.payload.name} error: ${evt.payload.error}` }
          : { level: 'info', message: `${evt.payload.name} finished` };
        return { ...s, activeAgents: next, log: [...s.log, logLine] };
      }

      case 'score_update':
        if (evt.payload.phase === 'before') {
          return { ...s, scoreBefore: evt.payload.value, missingKeywords: evt.payload.missing_keywords || [], matchedKeywords: evt.payload.matched_keywords || [] };
        } else {
          return { ...s, scoreAfter: evt.payload.value, matchedKeywords: evt.payload.matched_keywords || [], missingKeywords: evt.payload.missing_keywords || [] };
        }

      case 'deliverable': {
        const deliverables = { ...s.deliverables, [evt.payload.kind]: evt.payload };
        return { ...s, deliverables };
      }

      case 'token_usage':
        return { ...s, usage: evt.payload };

      case 'log':
        return { ...s, log: [...s.log, evt.payload] };

      case 'done':
        return { ...s, done: true, running: false };

      default:
        return s;
    }
  });
}

function _clearMockTimers() {
  _mockTimers.forEach(t => clearTimeout(t));
  _mockTimers = [];
}

export function connect(runId) {
  _clearMockTimers();
  if (_es) _es.close();
  const es = new EventSource(`${BACKEND}/events/${runId}`);
  _es = es;
  es.onmessage = (e) => {
    try { apply(JSON.parse(e.data)); } catch (_) {}
  };
  es.onerror = () => {
    state.update(s => ({ ...s, log: [...s.log, { level: 'error', message: 'SSE connection lost' }] }));
  };
  return () => { es.close(); _es = null; };
}

// Client-side mock replay — works fully offline, no server needed.
// Fetches /trace.json (bundled as a static asset in web/public/) and
// replays events on their delay_ms timeline using setTimeout.
export async function connectMockLocal() {
  _clearMockTimers();
  if (_es) { _es.close(); _es = null; }

  let events;
  try {
    const resp = await fetch('/trace.json');
    events = await resp.json();
  } catch (e) {
    state.update(s => ({ ...s, log: [...s.log, { level: 'error', message: `Failed to load trace.json: ${e}` }] }));
    return () => {};
  }

  let cumulative = 0;
  for (const raw of events) {
    const evt = { ...raw };
    const delay = evt.delay_ms || 0;
    delete evt.delay_ms;
    cumulative += delay;
    const t = setTimeout(() => apply(evt), cumulative);
    _mockTimers.push(t);
  }

  return () => _clearMockTimers();
}

export async function startLiveRun(resume, jobPosting) {
  const resp = await fetch(`${BACKEND}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume, job_posting: jobPosting }),
  });
  const { run_id } = await resp.json();
  return connect(run_id);
}
