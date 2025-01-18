<script lang="ts">
	import Card from "$lib/components/Card.svelte";
	import { onMount } from "svelte"
	import type { LatLngExpression, LatLngBoundsExpression, Map as LeafletMap, PolylineDecorator } from "leaflet"
	import L from "leaflet"
	import "leaflet/dist/leaflet.css"
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
		
	// MAP STUFF
	let map: LeafletMap
	const displayHeight = 700
	const imageHeight = data.height
	const imageWidth = data.width
	const bounds: LatLngBoundsExpression = [[0, 0], [imageHeight, imageWidth]]
	const center: LatLngExpression = [
		imageHeight / 2,
		imageWidth / 2,
	]
	const minZoom = Math.log2(displayHeight / imageHeight);
	
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
	let polyline: L.Polyline
	let decorator: PolylineDecorator
	$: latlngs = data.routes[instructionIndex]
	function initializeMap() {
		map = L.map("map", {
		crs: L.CRS.Simple,
		zoomControl: true,
		dragging: true,
		}).setView(center, minZoom);

		map.setMaxBounds(bounds);
		map.options.maxZoom = 2;
		map.options.minZoom = minZoom;
		map.fitBounds(bounds);

		fireIcon = L.divIcon({
		html: '<div class="text-red-500 text-6xl">🔥</div>',
		iconSize: [0, 0],
		iconAnchor: [40, 40],
		});

		L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map);

		setupMapClickHandler();
	}

	$: {
    if (map) {
      // Remove old polyline and decorator if they exist
      if (polyline) map.removeLayer(polyline);
      if (decorator) map.removeLayer(decorator);

      // Create new polyline and decorator with updated latlngs
      polyline = L.polyline(latlngs, { color: "red" }).addTo(map);
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


	function setupMapClickHandler() {
		map.on("click", (e) => {
		if (placingFire) {
			const { lat, lng } = e.latlng;
			fireYCoords += imageHeight - lat + ",";
			fireXCoords += lng + ",";
			const marker = L.marker([lat, lng], { icon: fireIcon }).addTo(map);
			fireMarkers.push(marker);
		}
		});
	}

	function clearFireMarkers() {
		fireMarkers.forEach((marker) => map.removeLayer(marker));
		fireMarkers = [];
		fireXCoords = "";
		fireYCoords = "";
	}

	// Initialize map on mount
	onMount(() => {
		initializeMap();
	});

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

	function handleSubmit() {
		setTimeout(() => {
			clearFireMarkers();
			placingFire = false;
		}, 100); // Adjust delay as needed
	}
</script>

<div class="flex flex-col items-center pr-10 pt-4 pb-0 h-[93vh]">
	<div class="flex w-full gap-8 items-start justify-center">
		<div class="h-screen">
			<a href="/add_floorplan">&#10094;</a>
		</div>
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
			</div>
			<div class="card p-4 mb-0 h-80 w-full overflow-auto">
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

		<div class="w-3/4 overflow-hidden">
			<div id="map" style="height: {displayHeight}px">
			</div>
		</div>
	</div>
</div>
<div class="w-full h-10 mr-10   flex justify-center ">
	<div class="w-3/4 text-center flex justify-end">
		<form method="post" class="flex justify-between items-start w-3/4 mr-4 gap-6" use:enhance onsubmit={handleSubmit}>
			<input type="hidden" name="x" bind:value={fireXCoords}>
			<input type="hidden" name="y" bind:value={fireYCoords}>
			<input type="text" class="input text-lg w-full text-center" name="description" bind:value={fireDescription} placeholder="Eg. It is an electrical fire with casualties including one burned and inhaling smoke.">
		</form>
	</div>
	<button class="text-5xl text-align-top  h-10" onclick={startFire}>🔥</button>
</div>

<style>
	#map {
		background-color: white;
	}
</style>