<script lang="ts">
	import Card from "$lib/components/Card.svelte";
	import { onMount, onDestroy } from "svelte"
	import { browser } from "$app/environment";
	import type { LatLngExpression, LatLngBoundsExpression, LatLngTuple } from "leaflet"

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
	const imageHeight = 549
	const imageWidth = 1063
	const bounds: LatLngBoundsExpression = [[0, 0], [imageHeight, imageWidth]]
	// @ts-ignore
	const center: LatLngExpression = bounds[1].map((x) => x!/2)
	const room1Coordinates: LatLngExpression[] = [
		[100, 100],
		[200, 100],
		[200, 200],
		[100, 200],
	]

	const room2Coordinates: LatLngExpression[] = [
		[300, 300],
		[400, 300],
		[400, 400],
		[300, 400],
	]



	onMount(async () => {
		if (browser) {
			const L = await import("leaflet"); // Dynamically import Leaflet
		

			map = L.map("map", {
				crs: L.CRS.Simple,
			}).setView(center, -1);
			map.setMaxBounds(bounds)
			L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map);
			map.fitBounds(bounds)

			const room1 = L.polygon(room1Coordinates, { color: "blue" }).addTo(map)
			const room2 = L.polygon(room2Coordinates, { color: "green" }).addTo(map)

			room1.on("click", () => alert("Room 1 clicked"))
    		room2.on("click", () => alert("Room 2 clicked"))
		}

		// CLOCK
		updateClock()
		interval = setInterval(updateClock, 1000)
	})

	onDestroy(() => {
		if (map) map.remove()

		if (interval) clearInterval(interval)
	})
  </script>

<div class="flex flex-col items-center p-10">
	<h1 class="text-8xl mb-3"><a href="https://github.com/bedminer1/LIQUIDITY_TRACKER/">STABLETIDE</a></h1>
	<p class="mb-8">{displayDate}</p>
	<nav class="underline text-left w-full mb-4">
		<a href="/add_floorplan">New Floorplan?</a>
	</nav>
	<!-- GRAPH AND ANALYSIS -->
	<div class="flex w-full gap-4 items-start h-[100vh]">
		<div class="flex flex-col gap-4">
			<Card
				{...{
					title: "Floor Info",
					body: "Block A, Level 5",
					subtitle: "Represents 1/10 of the ETF by JP Morgan",
					icon: "&#9814;"
				}}
			/>
		</div>

		<div class="w-full border-2">
			<div id="map" class="w-full h-screen"></div>
		</div>
	</div>
</div>