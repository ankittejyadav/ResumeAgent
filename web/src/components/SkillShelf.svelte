<script>
  export let skills = [];
  export let activeAgents = new Set();

  const ALL_SKILLS = ['resume-tailor','cover-letter','company-research','interview-prep','ats-scorer'];
  $: loaded = new Set(skills.map(s => s.name));
</script>

<div class="skill-shelf">
  <h3>Skills</h3>
  <div class="cards">
    {#each ALL_SKILLS as name}
      {@const skill = skills.find(s => s.name === name)}
      {@const isLoaded = loaded.has(name)}
      {@const isActive = activeAgents.has(name)}
      <div class="card" class:loaded={isLoaded} class:active={isActive} title={skill?.description || name}>
        <div class="name">{name}</div>
        {#if skill}
          <div class="model-badge" class:haiku={skill.model?.includes('haiku')}>
            {skill.model?.includes('haiku') ? 'Haiku' : 'Sonnet'}
          </div>
        {/if}
        {#if isActive}<div class="active-ring"/>{/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .skill-shelf h3 { margin: 0 0 10px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); }
  .cards { display: flex; flex-direction: column; gap: 6px; }
  .card {
    padding: 8px 10px; border-radius: 10px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    opacity: 0.35; transition: all 0.3s; position: relative;
    cursor: default;
  }
  .card.loaded { opacity: 0.75; border-color: rgba(255,255,255,0.15); }
  .card.active { opacity: 1; border-color: #22d3ee; background: rgba(34,211,238,0.08); box-shadow: 0 0 12px rgba(34,211,238,0.2); }
  .name { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); }
  .model-badge { font-size: 9px; margin-top: 2px; font-weight: 700; color: #818cf8; }
  .model-badge.haiku { color: #fb923c; }
  .active-ring {
    position: absolute; inset: -2px; border-radius: 11px;
    border: 1px solid #22d3ee;
    animation: ring 1.5s ease-in-out infinite;
    pointer-events: none;
  }
  @keyframes ring {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.8; }
  }
</style>
