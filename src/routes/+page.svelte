<script lang="ts">
	import Card from "$lib/components/Card.svelte";
	import { onMount, onDestroy } from "svelte"
	import { browser } from "$app/environment";
	import type { LatLngExpression, LatLngBoundsExpression } from "leaflet"

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

	// MAP STUFF
	let map: any
	let L: any
	let placingFire = false
	let fireIcon: any; // Custom fire icon

	const imageHeight = 400
	const imageWidth = 600
	const bounds: LatLngBoundsExpression = [[0, 0], [imageHeight, imageWidth]]
	const center: LatLngExpression = [
		imageHeight / 2,
		imageWidth / 2,
	]

	onMount(async () => {
		if (browser) {
			L = await import("leaflet"); // Dynamically import Leaflet
		
			const link = document.createElement("link");
			link.rel = "stylesheet";
			link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
			document.head.appendChild(link);
			map = L.map("map", {
				crs: L.CRS.Simple,
				zoomControl: false,
				dragging: true,
				zoom: 1,
			}).setView(center, 0);
			map.setMaxBounds(bounds)
			map.options.maxZoom = 3
			map.options.minZoom = 0.4
			fireIcon = L.divIcon({
				className: "fire-icon",
				html: "🔥", // Fire emoji
				iconSize: [24, 24], // Adjust size if necessary
				iconAnchor: [12, 12], // Center the icon
			})

			L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map)

			map.on("click", (e: any) => {
			if (placingFire) {
				const { lat, lng } = e.latlng;
				L.marker([lat, lng], { icon: fireIcon }).addTo(map); // Place marker at clicked location
				placingFire = false; // Exit "fire placing mode"
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
		<button onclick={startFire}>Start a fire? (demo)</button>
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
			<div id="map" class="h-[600px]"></div>
		</div>
	</div>
</div>