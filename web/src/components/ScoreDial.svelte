<script>
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  export let before = null;
  export let after = null;
  export let missingKeywords = [];
  export let matchedKeywords = [];

  const displayed = tweened(0, { duration: 1200, easing: cubicOut });
  $: if (after !== null) displayed.set(after);
  else if (before !== null) displayed.set(before);
  else displayed.set(0);

  const R = 60;
  const CIRC = 2 * Math.PI * R;
  $: arc = ($displayed / 100) * CIRC;
  $: color = $displayed >= 80 ? '#a3e635' : $displayed >= 50 ? '#22d3ee' : '#fb7185';
  $: delta = (before !== null && after !== null) ? after - before : null;
</script>

<div class="dial-wrap">
  <svg width="160" height="160" viewBox="0 0 160 160">
    <!-- track -->
    <circle cx="80" cy="80" r={R} fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="14"/>
    <!-- ghost (before) -->
    {#if before !== null && after !== null}
      <circle cx="80" cy="80" r={R} fill="none"
        stroke="rgba(255,255,255,0.18)" stroke-width="14"
        stroke-dasharray="{(before/100)*CIRC} {CIRC}"
        stroke-dashoffset="{CIRC/4}"
        stroke-linecap="round"
        transform="rotate(-90 80 80)"/>
    {/if}
    <!-- live arc -->
    <circle cx="80" cy="80" r={R} fill="none"
      stroke={color} stroke-width="14"
      stroke-dasharray="{arc} {CIRC}"
      stroke-dashoffset="{CIRC/4}"
      stroke-linecap="round"
      transform="rotate(-90 80 80)"
      style="transition: stroke 0.4s"/>
    <!-- centre text -->
    <text x="80" y="76" text-anchor="middle" class="pct" fill="white" font-size="22" font-weight="700">{Math.round($displayed)}%</text>
    {#if delta !== null}
      <text x="80" y="98" text-anchor="middle" class="delta" fill={delta >= 0 ? '#a3e635' : '#fb7185'} font-size="13">
        {delta >= 0 ? '+' : ''}{delta}
      </text>
    {/if}
  </svg>

  {#if before !== null || after !== null}
    <div class="phases">
      {#if before !== null}<span class="phase before">Before: {before}%</span>{/if}
      {#if after !== null}<span class="phase after">After: {after}%</span>{/if}
    </div>
  {/if}

  {#if missingKeywords.length || matchedKeywords.length}
    <div class="keywords">
      {#each matchedKeywords as kw}
        <span class="chip matched">{kw}</span>
      {/each}
      {#each missingKeywords as kw}
        <span class="chip missing">{kw}</span>
      {/each}
    </div>
  {/if}
</div>

<style>
  .dial-wrap { display: flex; flex-direction: column; align-items: center; gap: 8px; }
  .phases { display: flex; gap: 12px; font-size: 11px; color: rgba(255,255,255,0.5); }
  .phase.after { color: #a3e635; }
  .keywords { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; max-width: 220px; margin-top: 4px; }
  .chip { font-size: 10px; padding: 2px 6px; border-radius: 999px; font-weight: 600; }
  .chip.matched { background: rgba(163,230,53,0.15); color: #a3e635; border: 1px solid rgba(163,230,53,0.3); }
  .chip.missing { background: rgba(251,113,133,0.15); color: #fb7185; border: 1px solid rgba(251,113,133,0.3); }
  circle { transition: stroke-dasharray 0.8s cubic-bezier(0.4,0,0.2,1); }
</style>
