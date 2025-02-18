<script lang="ts">
	import '../app.css'
	import { ModeWatcher, toggleMode } from 'mode-watcher'
	import { Toaster } from "$lib/components/ui/sonner";
  	import Switch from '$lib/components/ui/switch/switch.svelte';
	let { children } = $props()

	let toggled = $state(false)

	$effect(() => {
		if (toggled) {}
		toggleMode()
	})
</script>

<Toaster />
<ModeWatcher />
<div class="p-2 w-full justify-end flex">
	<Switch bind:checked={toggled}/>
</div>
{@render children()}
