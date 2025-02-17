<script lang="ts">
    import type {Snippet} from "svelte";
    import * as Card from "$lib/components/ui/card";

    let {title, body, subtitle, icon, footer}: {
        title: string,
        body: string,
        subtitle?: string,
        icon?: string
        footer?: Snippet,
    } = $props()
</script>

<Card.Root>
    <div class="card p-4 w-full">
        <Card.Header>

        </Card.Header>
        <div class="flex w-full justify-between mb-5">
            <p>{ title }</p>
            {#if icon}
                <p class="text-3xl">{@html icon}</p>
            {/if}
        </div>
        <p class="text-2xl">{ body }</p>
        {#if subtitle}
            <p class="italic">{ subtitle }</p>
        {/if}
        {@render footer?.()}
    </div>
</Card.Root>