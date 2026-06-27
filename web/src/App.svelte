<script>
  import { state, connect, connectMock } from './lib/eventStore.js';
  import ScoreDial from './components/ScoreDial.svelte';
  import TodoPanel from './components/TodoPanel.svelte';
  import AgentGraph from './components/AgentGraph.svelte';
  import SkillShelf from './components/SkillShelf.svelte';
  import Deliverables from './components/Deliverables.svelte';
  import ActivityLog from './components/ActivityLog.svelte';

  let resume = '';
  let jobPosting = '';
  let mockMode = false;
  let view = 'input'; // 'input' | 'dashboard'
  let cleanup = null;

  const SAMPLE_RESUME = `# Alex Chen
alex.chen@email.com | github.com/alexchen | San Francisco, CA

## Summary
Software engineer with 4 years of experience building scalable backend systems and APIs.

## Experience

### Senior Software Engineer | Acme Corp | 2022–Present
- Built REST APIs serving 2M daily requests using Python and FastAPI
- Deployed microservices on AWS (EC2, Lambda, S3) with Docker and Kubernetes
- Implemented CI/CD pipelines with GitHub Actions, reducing deploy time by 60%
- Designed PostgreSQL schemas and Redis caching layer

### Software Engineer | StartupXYZ | 2020–2022
- Developed data pipelines processing 10TB/day with Apache Spark
- Built ML feature engineering platform using scikit-learn and PyTorch
- Collaborated cross-functionally with product and data science teams

## Skills
Python, FastAPI, Django, JavaScript, TypeScript, React, PostgreSQL, MongoDB, Redis,
Docker, Kubernetes, AWS, GCP, Git, CI/CD, Agile, Scrum`;

  const SAMPLE_JOB = `Senior Backend Engineer — AI Infrastructure
Anthropic, San Francisco, CA

About the role:
Join our AI infrastructure team to build the systems that power Claude.

Requirements (must have):
- 4+ years Python backend development
- Experience with FastAPI or similar async frameworks
- PostgreSQL and Redis expertise required
- Docker and Kubernetes (k8s) required
- CI/CD pipelines (GitHub Actions preferred)
- AWS or GCP cloud experience required

Preferred:
- LLM/AI experience (LangChain, RAG, fine-tuning)
- Distributed systems at scale
- Strong SQL skills
- Terraform or infrastructure-as-code

Responsibilities:
- Design and build APIs and microservices for AI products
- Collaborate with ML engineers to productionize models
- Own system reliability, monitoring, and on-call rotation`;

  function loadSample() {
    resume = SAMPLE_RESUME;
    jobPosting = SAMPLE_JOB;
  }

  async function forge() {
    if (cleanup) cleanup();
    if (mockMode) {
      view = 'dashboard';
      cleanup = connectMock();
    } else {
      const resp = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume, job_posting: jobPosting }),
      });
      const { run_id } = await resp.json();
      view = 'dashboard';
      cleanup = connect(run_id);
    }
  }

  function reset() {
    if (cleanup) cleanup();
    view = 'input';
  }
</script>

{#if view === 'input'}
  <div class="input-screen">
    <div class="header">
      <h1>JobForge <span class="spark">✦</span></h1>
      <p class="tagline">Paste resume + job posting → tailored kit in ~60s</p>
    </div>

    <div class="mode-row">
      <label class="toggle">
        <input type="checkbox" bind:checked={mockMode}/>
        <span class="slider"></span>
      </label>
      <span class="label">{mockMode ? 'MOCK' : 'LIVE'}</span>
      <span class="mode-hint">{mockMode ? 'Replays recorded trace (no API needed)' : 'Calls Claude API live'}</span>
    </div>

    <div class="inputs">
      <div class="field">
        <label for="resume">Resume</label>
        <textarea id="resume" bind:value={resume} placeholder="Paste your resume here…" rows="12"></textarea>
      </div>
      <div class="field">
        <label for="job">Job Posting</label>
        <textarea id="job" bind:value={jobPosting} placeholder="Paste the job posting here…" rows="12"></textarea>
      </div>
    </div>

    <div class="actions">
      <button class="sample-btn" on:click={loadSample}>Load Sample</button>
      <button class="forge-btn" on:click={forge} disabled={!mockMode && (!resume || !jobPosting)}>
        Forge ✦
      </button>
    </div>
  </div>

{:else}
  <div class="dashboard">
    <div class="dash-header">
      <span class="logo">JobForge ✦</span>
      <div class="hud">
        {#if $state.usage}
          <span class="cost">~${$state.usage.est_cost_usd.toFixed(4)} · {$state.usage.input_tokens + $state.usage.output_tokens} tok</span>
        {/if}
        <span class="badge" class:mock={mockMode}>{mockMode ? 'MOCK' : 'LIVE'}</span>
        {#if $state.done}<span class="badge done">DONE</span>{/if}
      </div>
      <button class="back-btn" on:click={reset}>← New Run</button>
    </div>

    <div class="dash-body">
      <div class="col-left">
        <div class="panel skill-panel"><SkillShelf skills={$state.skills} activeAgents={$state.activeAgents}/></div>
      </div>

      <div class="col-center">
        <div class="panel graph-panel"><AgentGraph skills={$state.skills} activeAgents={$state.activeAgents}/></div>
        <div class="todo-row">
          <div class="panel todo-wrap"><TodoPanel todos={$state.todos}/></div>
          <div class="panel log-wrap"><ActivityLog log={$state.log}/></div>
        </div>
      </div>

      <div class="col-right">
        <div class="panel score-panel">
          <h3>ATS Score</h3>
          <ScoreDial
            before={$state.scoreBefore}
            after={$state.scoreAfter}
            missingKeywords={$state.missingKeywords}
            matchedKeywords={$state.matchedKeywords}/>
        </div>
      </div>
    </div>

    <div class="deliverables-bar">
      <div class="panel deliverables-panel">
        <Deliverables deliverables={$state.deliverables}/>
      </div>
    </div>
  </div>
{/if}

<style>
  :global(*) { box-sizing: border-box; }
  :global(body) {
    margin: 0; padding: 0;
    background: radial-gradient(ellipse at 30% 20%, #0f172a 0%, #0a0f1e 60%, #000 100%);
    color: white; font-family: 'Inter', system-ui, sans-serif;
    min-height: 100vh; overflow: hidden;
  }

  .input-screen { max-width: 900px; margin: 0 auto; padding: 40px 24px; }
  .header { text-align: center; margin-bottom: 32px; }
  h1 { font-size: 42px; font-weight: 800; margin: 0; letter-spacing: -1px; }
  .spark { color: #22d3ee; }
  .tagline { color: rgba(255,255,255,0.4); margin: 8px 0 0; font-size: 15px; }

  .mode-row { display: flex; align-items: center; gap: 10px; margin-bottom: 24px; }
  .toggle { display: flex; align-items: center; cursor: pointer; }
  .toggle input { display: none; }
  .slider {
    width: 36px; height: 20px; background: rgba(255,255,255,0.1);
    border-radius: 10px; position: relative; transition: background 0.2s; display: block;
  }
  .slider::after {
    content: ''; position: absolute; top: 3px; left: 3px;
    width: 14px; height: 14px; border-radius: 7px; background: white; transition: left 0.2s;
  }
  .toggle input:checked + .slider { background: #22d3ee; }
  .toggle input:checked + .slider::after { left: 19px; }
  .label { font-size: 12px; font-weight: 700; color: #22d3ee; }
  .mode-hint { font-size: 12px; color: rgba(255,255,255,0.35); }

  .inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .field label { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(255,255,255,0.4); margin-bottom: 6px; }
  textarea {
    width: 100%; resize: vertical;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; color: white; font-size: 12px; padding: 12px;
    font-family: inherit; line-height: 1.6; transition: border-color 0.2s;
  }
  textarea:focus { outline: none; border-color: rgba(34,211,238,0.4); }

  .actions { display: flex; justify-content: center; gap: 16px; margin-top: 24px; }
  .sample-btn {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.7); padding: 12px 24px; border-radius: 12px;
    font-size: 14px; cursor: pointer; transition: all 0.2s;
  }
  .sample-btn:hover { background: rgba(255,255,255,0.1); }
  .forge-btn {
    background: linear-gradient(135deg, #22d3ee, #818cf8);
    border: none; color: white; padding: 12px 36px; border-radius: 12px;
    font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.2s;
    box-shadow: 0 4px 20px rgba(34,211,238,0.3);
  }
  .forge-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 28px rgba(34,211,238,0.4); }
  .forge-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .dashboard { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
  .dash-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(0,0,0,0.3); backdrop-filter: blur(8px); flex-shrink: 0;
  }
  .logo { font-weight: 800; font-size: 16px; color: #22d3ee; }
  .hud { display: flex; gap: 8px; align-items: center; }
  .cost { font-size: 11px; color: rgba(255,255,255,0.35); font-family: monospace; }
  .badge {
    font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px;
    background: rgba(34,211,238,0.15); color: #22d3ee; border: 1px solid rgba(34,211,238,0.3);
  }
  .badge.mock { background: rgba(251,146,60,0.15); color: #fb923c; border-color: rgba(251,146,60,0.3); }
  .badge.done { background: rgba(163,230,53,0.15); color: #a3e635; border-color: rgba(163,230,53,0.3); }
  .back-btn {
    background: none; border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.5);
    padding: 4px 12px; border-radius: 6px; font-size: 11px; cursor: pointer; transition: all 0.2s;
  }
  .back-btn:hover { border-color: rgba(255,255,255,0.3); color: white; }

  .dash-body { display: flex; flex: 0 0 340px; overflow: hidden; }
  .col-left, .col-right { width: 210px; flex-shrink: 0; display: flex; flex-direction: column; }
  .col-center { flex: 1; display: flex; flex-direction: column; min-width: 0; }

  .panel {
    background: rgba(255,255,255,0.03); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06); margin: 6px; border-radius: 16px; padding: 14px;
  }
  .panel h3 { margin: 0 0 12px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); }

  .skill-panel { flex: 1; overflow-y: auto; }
  .graph-panel { flex: 1; display: flex; align-items: center; justify-content: center; padding: 4px; }
  .todo-row { display: flex; flex-shrink: 0; height: 130px; }
  .todo-wrap, .log-wrap { flex: 1; overflow: hidden; }
  .score-panel { flex: 1; display: flex; flex-direction: column; align-items: center; overflow-y: auto; }

  .deliverables-bar { flex: 1; min-height: 0; overflow: hidden; }
  .deliverables-panel { height: calc(100% - 12px); overflow: hidden; display: flex; flex-direction: column; }
</style>
