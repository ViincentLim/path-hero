<script lang="ts">
    import type {Snippet} from "svelte";

    let {title, body, subtitle, icon, footer}: {
        title: string,
        body: string,
        subtitle?: string,
        icon?: string
        footer: Snippet,
    } = $props()
</script>

<div class="card p-4 w-full">
    <div class="flex w-full justify-between mb-5">
        <p>{ title }</p>
        {#if icon}
            <p class="text-3xl">{@html icon}</p>
        {/if}
    </div>
    <p class="text-2xl">{ body }</p>
    {#if subtitle}
        <p class="italic text-gray-400">{ subtitle }</p>
    {/if}
    {@render footer?.()}
</div>