<script>
  export let skills = [];
  export let activeAgents = new Set();

  const CX = 200, CY = 160;
  const RADIUS = 110;

  function nodePos(i, total) {
    const angle = (i / total) * Math.PI * 2 - Math.PI / 2;
    return { x: CX + RADIUS * Math.cos(angle), y: CY + RADIUS * Math.sin(angle) };
  }

  $: positions = skills.map((_, i) => nodePos(i, skills.length || 5));
  $: skillActive = (name) => activeAgents.has(name);
</script>

<svg width="400" height="320" viewBox="0 0 400 320" class="agent-graph">
  <!-- Edges -->
  {#each skills as skill, i}
    {@const pos = positions[i]}
    <line x1={CX} y1={CY} x2={pos.x} y2={pos.y}
      stroke={skillActive(skill.name) ? '#22d3ee' : 'rgba(255,255,255,0.08)'}
      stroke-width={skillActive(skill.name) ? 2 : 1}
      class={skillActive(skill.name) ? 'edge-pulse' : ''}/>
  {/each}

  <!-- Orchestrator node -->
  <circle cx={CX} cy={CY} r="28" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" stroke-width="2"/>
  <text x={CX} y={CY-4} text-anchor="middle" fill="#22d3ee" font-size="9" font-weight="700">MAESTRO</text>
  <text x={CX} y={CY+8} text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="7">orchestrator</text>

  <!-- Subagent nodes -->
  {#each skills as skill, i}
    {@const pos = positions[i]}
    {@const active = skillActive(skill.name)}
    {@const loaded = skills.length > 0}
    <circle cx={pos.x} cy={pos.y} r="22"
      fill={active ? 'rgba(34,211,238,0.15)' : loaded ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.02)'}
      stroke={active ? '#22d3ee' : loaded ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.06)'}
      stroke-width={active ? 2 : 1}
      class={active ? 'node-pulse' : ''}/>
    <text x={pos.x} y={pos.y+2} text-anchor="middle" fill={active ? '#22d3ee' : 'rgba(255,255,255,0.6)'}
      font-size="7" font-weight="600">
      {skill.name.replace('-', '​-')}
    </text>
    <text x={pos.x} y={pos.y+12} text-anchor="middle"
      fill={skill.model?.includes('haiku') ? '#fb923c' : '#818cf8'}
      font-size="6">
      {skill.model?.includes('haiku') ? 'Haiku' : 'Sonnet'}
    </text>
  {/each}
</svg>

<style>
  .agent-graph { display: block; }
  .edge-pulse { animation: edgePulse 1.2s ease-in-out infinite; }
  .node-pulse { animation: nodePulse 1.5s ease-in-out infinite; }
  @keyframes edgePulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
  }
  @keyframes nodePulse {
    0%, 100% { filter: drop-shadow(0 0 4px rgba(34,211,238,0.4)); }
    50% { filter: drop-shadow(0 0 12px rgba(34,211,238,0.8)); }
  }
</style>
