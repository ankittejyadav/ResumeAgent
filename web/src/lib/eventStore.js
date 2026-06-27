import { writable } from 'svelte/store';

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
  runId: null,
});

let _es = null;

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

export function connect(runId) {
  if (_es) _es.close();
  const es = new EventSource(`http://localhost:8000/events/${runId}`);
  _es = es;
  es.onmessage = (e) => {
    try { apply(JSON.parse(e.data)); } catch (_) {}
  };
  es.onerror = () => {
    state.update(s => ({ ...s, log: [...s.log, { level: 'error', message: 'SSE connection lost' }] }));
  };
  return () => es.close();
}

export function connectMock() {
  if (_es) _es.close();
  // Use the server's /mock endpoint — it paces events with delay_ms server-side
  const es = new EventSource(`http://localhost:8000/mock`);
  _es = es;
  es.onmessage = (e) => {
    try { apply(JSON.parse(e.data)); } catch (_) {}
  };
  es.onerror = () => {
    state.update(s => ({ ...s, log: [...s.log, { level: 'error', message: 'Mock SSE error' }] }));
  };
  return () => es.close();
}

export function connectMockLocal(traceEvents) {
  // Replay trace.json locally with delay_ms (works fully offline)
  let i = 0;
  function fireNext() {
    if (i >= traceEvents.length) return;
    const evt = { ...traceEvents[i] };
    const delay = evt.delay_ms || 0;
    delete evt.delay_ms;
    setTimeout(() => {
      apply(evt);
      i++;
      fireNext();
    }, delay);
  }
  fireNext();
}
