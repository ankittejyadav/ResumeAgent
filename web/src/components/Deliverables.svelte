<script>
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  export let deliverables = {};

  const TABS = [
    { kind: 'tailored_resume', label: 'Resume' },
    { kind: 'cover_letter', label: 'Cover Letter' },
    { kind: 'company_research', label: 'Company' },
    { kind: 'interview_prep', label: 'Interview' },
  ];

  let activeTab = 'tailored_resume';
  $: available = TABS.filter(t => deliverables[t.kind]);
  $: if (available.length && !deliverables[activeTab]) activeTab = available[0]?.kind;

  function renderMd(md) {
    return DOMPurify.sanitize(marked.parse(md || ''));
  }

  function copy(kind) {
    const d = deliverables[kind];
    if (d) navigator.clipboard.writeText(d.content_markdown);
  }
</script>

<div class="deliverables">
  <div class="tabs">
    {#each TABS as tab}
      <button class="tab" class:active={activeTab === tab.kind}
        class:ready={!!deliverables[tab.kind]}
        on:click={() => activeTab = tab.kind}>
        {tab.label}
        {#if deliverables[tab.kind]}<span class="dot">●</span>{/if}
      </button>
    {/each}
  </div>

  <div class="content">
    {#each TABS as tab}
      {#if activeTab === tab.kind}
        {#if deliverables[tab.kind]}
          <div class="toolbar">
            <span class="title">{deliverables[tab.kind].title}</span>
            <button class="copy-btn" on:click={() => copy(tab.kind)}>Copy</button>
          </div>
          <div class="markdown">
            {@html renderMd(deliverables[tab.kind].content_markdown)}
          </div>
        {:else}
          <div class="empty">Waiting for {tab.label.toLowerCase()}…</div>
        {/if}
      {/if}
    {/each}
  </div>
</div>

<style>
  .deliverables { display: flex; flex-direction: column; height: 100%; }
  .tabs { display: flex; gap: 2px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 4px; }
  .tab {
    background: none; border: none; color: rgba(255,255,255,0.35);
    font-size: 12px; padding: 4px 10px; border-radius: 6px; cursor: pointer;
    transition: all 0.2s; position: relative;
  }
  .tab.ready { color: rgba(255,255,255,0.65); }
  .tab.active { color: #22d3ee; background: rgba(34,211,238,0.08); }
  .dot { position: absolute; top: 2px; right: 2px; font-size: 5px; color: #a3e635; }
  .content { flex: 1; overflow-y: auto; padding: 12px 4px; }
  .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .title { font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.5); }
  .copy-btn {
    background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.3);
    color: #22d3ee; font-size: 11px; padding: 3px 10px; border-radius: 6px;
    cursor: pointer; transition: all 0.2s;
  }
  .copy-btn:hover { background: rgba(34,211,238,0.2); }
  .markdown { font-size: 12px; line-height: 1.65; color: rgba(255,255,255,0.8); }
  :global(.markdown h1, .markdown h2, .markdown h3) { color: white; margin: 8px 0 4px; }
  :global(.markdown ul, .markdown ol) { padding-left: 18px; }
  :global(.markdown li) { margin: 2px 0; }
  :global(.markdown p) { margin: 4px 0; }
  :global(.markdown code) { background: rgba(255,255,255,0.08); padding: 1px 4px; border-radius: 3px; font-size: 11px; }
  :global(.markdown pre) { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; overflow-x: auto; }
  .empty { color: rgba(255,255,255,0.25); font-style: italic; font-size: 12px; padding: 20px 0; text-align: center; }
</style>
