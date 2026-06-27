<script>
  import { afterUpdate } from 'svelte';
  export let log = [];

  let container;
  afterUpdate(() => {
    if (container) container.scrollTop = container.scrollHeight;
  });
</script>

<div class="activity-log" bind:this={container}>
  {#each log as entry, i}
    <div class="line level-{entry.level}">
      <span class="ts">{i + 1}</span>
      <span class="msg">{entry.message}</span>
    </div>
  {/each}
  {#if log.length === 0}
    <div class="empty">Activity will appear here…</div>
  {/if}
</div>

<style>
  .activity-log {
    height: 100%; overflow-y: auto; font-size: 11px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    display: flex; flex-direction: column; gap: 2px;
  }
  .line { display: flex; gap: 8px; padding: 2px 0; }
  .ts { color: rgba(255,255,255,0.2); min-width: 20px; text-align: right; }
  .level-info .msg { color: rgba(255,255,255,0.6); }
  .level-warn .msg { color: #fbbf24; }
  .level-error .msg { color: #fb7185; }
  .empty { color: rgba(255,255,255,0.2); font-style: italic; }
</style>
