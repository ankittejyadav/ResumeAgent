<script>
  import { flip } from 'svelte/animate';
  import { fade } from 'svelte/transition';
  export let todos = [];
</script>

<div class="todo-panel">
  <h3>Plan</h3>
  <ul>
    {#each todos as todo (todo.id)}
      <li animate:flip={{ duration: 300 }} transition:fade class="todo status-{todo.status}">
        <span class="icon">
          {#if todo.status === 'done'}✓{:else if todo.status === 'in_progress'}<span class="spin">◐</span>{:else}○{/if}
        </span>
        <span class="title">{todo.title}</span>
      </li>
    {/each}
    {#if todos.length === 0}
      <li class="empty">Waiting for plan…</li>
    {/if}
  </ul>
</div>

<style>
  .todo-panel h3 { margin: 0 0 10px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); }
  ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
  li { display: flex; align-items: center; gap: 8px; font-size: 13px; padding: 6px 8px; border-radius: 8px; background: rgba(255,255,255,0.03); transition: background 0.3s; }
  .status-done { color: #a3e635; }
  .status-in_progress { color: #22d3ee; background: rgba(34,211,238,0.06); }
  .status-pending { color: rgba(255,255,255,0.4); }
  .icon { width: 16px; text-align: center; font-size: 14px; }
  .spin { display: inline-block; animation: spin 1s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty { color: rgba(255,255,255,0.2); font-style: italic; font-size: 12px; }
</style>
