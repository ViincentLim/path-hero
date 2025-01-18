<script lang="ts">
	import Card from "$lib/components/Card.svelte";
	import { onMount, onDestroy } from "svelte"
	import { browser } from "$app/environment";
	import type { LatLngExpression, LatLngBoundsExpression, Map as LeafletMap } from "leaflet"

	// CLOCK STUFF
	function formatDate(dateString: string): string {
		const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		const [year, month, day] = dateString.split("-");
		const monthShort = months[parseInt(month, 10) - 1];
		return `${parseInt(day, 10)} ${monthShort} ${year}`;
	}

	let time = ""
	function updateClock() {
		const now = new Date()
		const hours = now.getHours().toString().padStart(2, "0")
		const minutes = now.getMinutes().toString().padStart(2, "0")
		const seconds = now.getSeconds().toString().padStart(2, "0")
		time = `${hours}:${minutes}:${seconds}`
	}
	$: displayDate = time + " | " + formatDate("2025-01-18")
	let interval: ReturnType<typeof setInterval>

	// Height of map in px
	const displayHeight = 700;

	// MAP STUFF
	let map: LeafletMap
	let L: any
	let placingFire = false
	let fireIcon: any; // Custom fire icon

	const imageHeight = 1414
	const imageWidth = 2000
	const bounds: LatLngBoundsExpression = [[0, 0], [imageHeight, imageWidth]]
	const center: LatLngExpression = [
		imageHeight / 2,
		imageWidth / 2,
	]
	let fireXCoords: string = ""
	let fireYCoords: string = ""
	let fireDescription: string

	onMount(async () => {
		if (browser) {
			L = await import("leaflet"); // Dynamically import Leaflet

			const link = document.createElement("link");
			link.rel = "stylesheet";
			link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
			document.head.appendChild(link);
			const minZoom = Math.log2(displayHeight/imageHeight);
			map = L.map("map", {
				crs: L.CRS.Simple,
				zoomControl: true,
				dragging: true,
			}).setView(center, minZoom);
			map.setMaxBounds(bounds);
			map.options.maxZoom = 2
			map.options.minZoom = minZoom
			map.fitBounds(bounds);
			fireIcon = L.divIcon({
				html: '<div class="text-red-500 text-6xl">🔥</div>',
				iconSize: [0, 0], // Adjust size if necessary
				iconAnchor: [40, 40], // Center the icon
			})

			L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map)

			map.on("click", (e: any) => {
			if (placingFire) {
				const { lat, lng } = e.latlng;
				fireYCoords += lat + ","
				fireXCoords += lng + ","
				L.marker([lat, lng], { icon: fireIcon }).addTo(map); // Place marker at clicked location
				}
			});
		}

		// CLOCK
		updateClock()
		interval = setInterval(updateClock, 1000)
	})

	onDestroy(() => {
		if (map) map.remove()

		if (interval) clearInterval(interval)
	})

	// FIRE
	function startFire() {
		placingFire = true
	}
  </script>

<div class="flex flex-col items-center p-10">
	<h1 class="text-4xl mb-1"><a href="https://github.com/ViincentLim/path-hero">PATH HERO</a></h1>
	<p class="mb-8">{displayDate}</p>
	<nav class="underline text-left w-full mb-4">
		<a href="/add_floorplan">New Floorplan?</a>
		{#if !placingFire}
		<button onclick={startFire}>Start a fire? (demo)</button>
		{:else}
		<form method="post">
			<input type="hidden" name="x" bind:value={fireXCoords}>
			<input type="hidden" name="y" bind:value={fireYCoords}>
			<input type="text" class="input" name="description" bind:value={fireDescription}>
			<button>Start Burning</button>
		</form>
		{/if}
	</nav>
	<div class="flex w-full gap-4 items-start">
		<div class="flex flex-col gap-4">
			<Card
				{...{
					title: "Floor Info",
					body: "Block A, Level 5",
					subtitle: "Hospital Ward",
					icon: "&#9814;"
				}}
			/>
		</div>

		<div class="w-3/4 overflow-hidden">
			<div id="map" style="height: {displayHeight}px"></div>
		</div>
	</div>
</div>