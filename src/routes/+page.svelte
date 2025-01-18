<script lang="ts">
	import Card from "$lib/components/Card.svelte";
	import { onMount, onDestroy } from "svelte"
	import { browser } from "$app/environment";
	import type { LatLngExpression, LatLngBoundsExpression, Map as LeafletMap, PolylineDecorator } from "leaflet"
	import L from "leaflet"
  import { enhance } from "$app/forms";
	import('leaflet-polylinedecorator')

	export let data: {
	  height: number,
      width: number,
      rooms: LatLngExpression[],
      extinguisherPowder: LatLngExpression[],
      extinguisherCo2: LatLngExpression[],
      extinguisherFoam: LatLngExpression[],
      exits: LatLngExpression[], 
	  instructions: string[],
	  routes: LatLngExpression[][]
	}

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
	$: displayDate = time + " | " + formatDate("2025-01-19")
	let interval: ReturnType<typeof setInterval>

	// Height of map in px
	const displayHeight = 700;

	// MAP STUFF
	let map: LeafletMap
	
	const imageHeight = data.height
	const imageWidth = data.width
	const bounds: LatLngBoundsExpression = [[0, 0], [imageHeight, imageWidth]]
	const center: LatLngExpression = [
		imageHeight / 2,
		imageWidth / 2,
	]
	
	//FIRE
	let placingFire = false
	let fireIcon: any
	let fireXCoords: string = ""
	let fireYCoords: string = ""
	let fireDescription: string
	let fireMarkers: L.Marker[] = []
	function startFire() {
		placingFire = true
	}


	// PATH
	let instructionIndex = 0
	$: latlngs = data.routes[instructionIndex]
	let polyline: L.Polyline
	let decorator: PolylineDecorator
	$: {
		if (map && polyline && decorator) {
			// Remove old polyline and decorator
			map.removeLayer(polyline);
			map.removeLayer(decorator);

			// Add new polyline with updated latlngs
			polyline = L.polyline(latlngs, { color: "red" }).addTo(map);

			// Add updated decorator
			decorator = L.polylineDecorator(polyline, {
				patterns: [
					{
						offset: "100%",
						repeat: 0,
						symbol: L.Symbol.arrowHead({
							pixelSize: 20,
							pathOptions: { color: "red", fillOpacity: 1 },
						}),
					},
				],
			}).addTo(map);
		}
	}



	onMount(async () => {
		if (browser) {
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

			// for (let exit of data.exits) {
			// 	const marker = L.circleMarker(exit, {
			// 		radius: 40,
			// 		color: "transparent", // Makes the border invisible
			// 		fillColor: "transparent", // Makes the fill invisible
			// 		fillOpacity: 0, // Ensures no visible fill
			// 	}).addTo(map)
			// 	marker.bindTooltip("This is an exit", {
			// 		permanent: false, // Tooltip shows only on hover
			// 		direction: "top", // Position of the tooltip
			// 	})
			// }

			// for (let extinguishers of data.extinguisherFoam) {
			// 	const marker = L.circleMarker(extinguishers, {
			// 		radius: 40,
			// 		color: "transparent", // Makes the border invisible
			// 		fillColor: "transparent", // Makes the fill invisible
			// 		fillOpacity: 0, // Ensures no visible fill
			// 	}).addTo(map)
			// 	marker.bindTooltip("This is a foam extinguisher", {
			// 		permanent: false, // Tooltip shows only on hover
			// 		direction: "top", // Position of the tooltip
			// 	})
			// }

			// load map
			L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map)
			polyline = L.polyline(latlngs, {color: 'red'}).addTo(map)
			decorator = L.polylineDecorator(polyline, {
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
				const { lat, lng } = e.latlng
				fireYCoords += (imageHeight - (lat as number)) + ","
				fireXCoords += lng + ","
				const marker = L.marker([lat, lng], { icon: fireIcon }).addTo(map)
				fireMarkers.push(marker)
				}
			})
		}
		})

		function clearFireMarkers() {
			for (const marker of fireMarkers) {
				map.removeLayer(marker); // Remove each marker from the map
			}
			fireMarkers = []; // Reset the markers array
			fireXCoords = ""; // Clear fire coordinates
			fireYCoords = ""; // Clear fire coordinates
			fireDescription = ""; // Reset description input
		}

		function handleSubmit() {
			setTimeout(() => {
				clearFireMarkers();
				placingFire = false;
			}, 100); // Adjust delay as needed
		}
  </script>

<div class="flex flex-col items-center px-10 py-4">
	<!-- <h1 class="text-4xl mb-1"><a href="https://github.com/ViincentLim/path-hero">PATH HERO</a></h1>
	<p class="mb-8">{displayDate}</p> -->
	<nav class="underline text-left w-full mb-4 pl-20">
		<a href="/add_floorplan">New Floorplan?</a>
	</nav>
	<div class="flex w-full gap-8 items-start justify-center">
		<div class="flex flex-col gap-4 w-1/6">
			<Card
				{...{
					title: "Floor Info",
					body: "Hospital Ward",
					subtitle: "Block A, Level 5",
					icon: "🗺️"
				}}
			/>
			<div class="card p-4 h-44 w-full">
				<div class="flex w-full justify-between mb-5">
					<p>Start a fire?</p> 
					<p class="text-3xl">🔥</p>
				</div>
				{#if !placingFire}
				<button class="button variant-ghost-primary p-3 text-2xl" onclick={startFire}>Place Fires</button>
				<p class="italic text-gray-400">Click map</p>
				{:else}
				<form method="post" class="flex flex-col justify-between items-start w-32" use:enhance onsubmit={handleSubmit}>
					<input type="hidden" name="x" bind:value={fireXCoords}>
					<input type="hidden" name="y" bind:value={fireYCoords}>
					<input type="text" class="input text-2xl" name="description" bind:value={fireDescription} placeholder="Describe">
					<button class="italic text-gray-400">Continue</button>
				</form>
				{/if}
			</div>
			<div class="card p-4 h-80 w-full overflow-auto">
				<div class="flex justify-between items-start">
					<h1 class="text-3xl mb-3">Instructions</h1>
					{#if instructionIndex < data.instructions.length-1}
					<button class="text-2xl underline" onclick={()=> instructionIndex++}>&#9758;</button>
					{:else}
					<button class="text-2xl underline" onclick={()=> instructionIndex--}>&#9756;</button>
					{/if}
				</div>
				<p>{data.instructions[instructionIndex]}</p>
			</div>
		</div>

		<div class="w-3/4 overflow-hidden border-2 border-dashed p-1 rounded-md">
			<div id="map" style="height: {displayHeight}px">
			</div>
		</div>
	</div>
</div>