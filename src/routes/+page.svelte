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

	//FIRE
	let fireXCoords: string = ""
	let fireYCoords: string = ""
	let fireDescription: string

	// PATH
	let latlngs = [[700, 700], [700, 710], [690, 710], [680, 710], [670, 710], [660, 710],
[650, 710], [650, 720], [640, 720], [640, 730], [640, 740], [640, 750],
[640, 760], [630, 760], [630, 770], [620, 770], [620, 760], [620, 750],
[610, 750], [600, 750], [600, 760], [600, 770], [600, 780], [590, 780],
[590, 770], [580, 770], [580, 760], [590, 760], [590, 750], [580, 750],
[580, 740], [570, 740], [570, 750], [560, 750], [560, 760], [570, 760],
[570, 770], [560, 770], [560, 780], [560, 790], [570, 790], [570, 780],
[580, 780], [580, 790], [580, 800], [590, 800], [600, 800], [600, 810],
[600, 820], [600, 830], [610, 830], [620, 830], [620, 840], [630, 840],
[640, 840], [650, 840], [650, 830], [660, 830], [670, 830], [680, 830],
[690, 830], [690, 820], [700, 820], [710, 820], [710, 830], [710, 840],
[720, 840], [730, 840], [730, 830], [720, 830], [720, 820], [720, 810],
[720, 800], [710, 800], [710, 790], [720, 790], [730, 790], [730, 780],
[720, 780], [720, 770], [710, 770], [710, 760], [720, 760], [730, 760],
[740, 760], [740, 750], [750, 750], [750, 760], [760, 760], [760, 750],
[760, 740], [750, 740], [740, 740], [740, 730], [750, 730], [750, 720],
[760, 720], [760, 710], [760, 700], [760, 690]]


	onMount(async () => {
		if (browser) {
			L = await import("leaflet")
			// @ts-ignore
			let polylineDecorator = import('leaflet-polylinedecorator')

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

			// load map
			L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map)
			let polyline = L.polyline(latlngs, {color: 'red'}).addTo(map)
				L.polylineDecorator(polyline, {
					patterns: [
						{
							offset: '100%',
							repeat: 0,
							symbol: L.Symbol.arrowHead({pixelSize: 20, pathOptions: {color: 'red', fillOpacity: 1}}),
						},
					],
				}).addTo(map)

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