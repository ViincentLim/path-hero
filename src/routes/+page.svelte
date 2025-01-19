<script lang="ts">
    import Card from "$lib/components/Card.svelte";
    import {onMount} from "svelte"
    import type {LatLngExpression, LatLngBoundsExpression, Map as LeafletMap, PolylineDecorator} from "leaflet"
    import L from "leaflet"
    import "leaflet/dist/leaflet.css"
    import {enhance} from "$app/forms"
    import 'leaflet-polylinedecorator'


    export let data: {
        height: number,
        width: number,
        rooms: Room[],
        extinguisherPowder: LatLngExpression[],
        extinguisherCo2: LatLngExpression[],
        extinguisherFoam: LatLngExpression[],
        exits: LatLngExpression[],
        hoseReel: LatLngExpression[],
        instructions: string[],
        routes: LatLngExpression[][],
        name: string,
        description: string,
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
        }).setView(center, minZoom)

        map.setMaxBounds(bounds);
        map.options.maxZoom = 2;
        map.options.minZoom = minZoom;
        map.fitBounds(bounds)

        fireIcon = L.divIcon({
            html: '<div class="text-red-500 text-6xl">🔥</div>',
            iconSize: [0, 0],
            iconAnchor: [40, 40],
        })

        L.imageOverlay("/images/floor/hospital_simple.png", bounds).addTo(map);

        setupMapClickHandler()

        for (let exit of data.exits) {
            createMarkerWithTooltip(exit, "This is an exit");
        }
        for (let extinguisher of data.extinguisherFoam) {
            createMarkerWithTooltip(extinguisher, "This is a foam extinguisher");
        }
        for (let extinguisher of data.extinguisherFoam) {
            createMarkerWithTooltip(extinguisher, "This is a foam extinguisher");
        }
        for (let extinguisher of data.extinguisherCo2) {
            createMarkerWithTooltip(extinguisher, "This is a CO2 extinguisher");
        }
        for (let extinguisher of data.extinguisherPowder) {
            createMarkerWithTooltip(extinguisher, "This is a powder extinguisher");
        }
        for (let hose of data.hoseReel) {
            createMarkerWithTooltip(hose, "This is a hose reel");
        }
        // for (let room of data.rooms) {
        // 	createMarkerWithTooltip(room.coords as LatLngExpression, `This is ${room.name}`);
        // }
        initializeRoomPolylines(data.rooms, map)
    }

    $: {
        if (map) {
            // Remove old polyline and decorator if they exist
            if (polyline) map.removeLayer(polyline);
            if (decorator) map.removeLayer(decorator);

            // Create new polyline and decorator with updated latlngs
            polyline = L.polyline(latlngs, {color: "red"}).addTo(map);
            decorator = L.polylineDecorator(polyline, {
                patterns: [
                    {
                        offset: "100%",
                        repeat: 0,
                        symbol: L.Symbol.arrowHead({
                            pixelSize: 20,
                            pathOptions: {color: "red", fillOpacity: 1},
                        }),
                    },
                ],
            }).addTo(map);
        }
    }

    function initializeRoomPolylines(rooms: Room[], map: L.Map) {
        rooms.forEach((room) => {
            // Create a polyline for the room's route
            const polyline = L.polyline(room.route as LatLngExpression[], {
                color: "green",
                weight: 4,
                dashArray: "5, 10", // Optional: Dashed line style
            }).addTo(map);

            // Add an arrowhead to the polyline using the Leaflet.PolylineDecorator plugin
            // const arrowHead = L.polylineDecorator(polyline, {
            //   patterns: [
            //     {
            //       offset: "100%", // Arrow at the end
            //       repeat: 0, // No repetition
            //       symbol: L.Symbol.arrowHead({
            //         pixelSize: 15,
            //         polygon: true,
            //         pathOptions: { fillColor: "green", fillOpacity: 1, stroke: true, weight: 1 },
            //       }),
            //     },
            //   ],
            // }).addTo(map);

            // Hide the polyline and arrowhead by default
            polyline.setStyle({opacity: 0});
            // arrowHead.setStyle({ opacity: 0 });

            // Create a marker for the room at its coordinates
            const marker = L.circleMarker(room.coords as LatLngExpression, {
                radius: 30,
                color: "transparent",
                fillColor: "transparent",
                fillOpacity: 1,
            }).addTo(map);

            // On hover, show the polyline and arrowhead
            marker.on("mouseover", () => {
                polyline.setStyle({opacity: 1});
                // arrowHead.setStyle({ opacity: 1 });
            });

            // On mouseout, hide the polyline and arrowhead
            marker.on("mouseout", () => {
                polyline.setStyle({opacity: 0});
                // arrowHead.setStyle({ opacity: 0 });
            });

            // Optionally bind a tooltip to the marker
            // marker.bindTooltip(room.name, {
            //   permanent: false,
            //   direction: "top",
            // });
        });
    }

    function setupMapClickHandler() {
        map.on("click", (e) => {
            if (placingFire) {
                const {lat, lng} = e.latlng;
                fireYCoords += imageHeight - lat + ",";
                fireXCoords += lng + ",";
                const marker = L.marker([lat, lng], {icon: fireIcon}).addTo(map);
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
        initializeMap()
    });

    function createMarkerWithTooltip(location: LatLngExpression, tooltipText: string) {
        const marker = L.circleMarker(location, {
            radius: 40,
            color: "transparent",
            fillColor: "transparent",
            fillOpacity: 0, // Ensures no visible fill
        }).addTo(map);

        console.log(location)

        marker.bindTooltip(tooltipText, {
            permanent: false, // Tooltip shows only on hover
            direction: "top", // Position of the tooltip
        });
    }

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

        <div class="w-3/4 overflow-hidden">
            <div id="map" style="height: {displayHeight}px">
            </div>
        </div>

        <div class="flex flex-col gap-4 w-1/6">
            <Card
                    {...{
                        title: "Floor Info",
                        body: data.name,
                        subtitle: data.description,
                        icon: "🗺️"
                    }}
            />
            <div class="card p-4 h-44 w-full">
            </div>
            <!--{#snippet instructions_footer()}-->
            <!--    {#if instructionIndex > 0}-->
            <!--        <button class="bg-transparent text-black p-2" style="border-radius: 8px; border: 1px solid black;"-->
            <!--                onclick={()=> instructionIndex&#45;&#45;}>Back-->
            <!--        </button>-->
            <!--    {/if}-->
            <!--    {#if instructionIndex < data.instructions.length - 1}-->
            <!--        <button class="bg-black text-white p-2" style="border-radius: 8px; border: 1px solid black;"-->
            <!--                onclick={()=> instructionIndex++}>Next-->
            <!--        </button>-->
            <!--    {/if}-->
            <!--{/snippet}-->
            <!--            Moved the card to below the map-->
            <!--            <Card title="Instructions" ,-->
            <!--                  body={data.instructions[instructionIndex]}-->
            <!--                  footer={instructions_footer}-->
            <!--            />-->
            <!--            <div class="card p-4 mb-0 h-80 w-full overflow-auto">-->
            <!--                <div class="flex justify-between items-start">-->
            <!--                    &lt;!&ndash;					<h1 class="text-3xl mb-3">Instructions</h1>&ndash;&gt;-->
            <!--                    <p>Instructions</p>-->
            <!--                    {#if instructionIndex < data.instructions.length - 1}-->
            <!--                        <button class="text-2xl underline" onclick={()=> instructionIndex++}>&#9758;</button>-->
            <!--                    {:else}-->
            <!--                        <button class="text-2xl underline" onclick={()=> instructionIndex&#45;&#45;}>&#9756;</button>-->
            <!--                    {/if}-->
            <!--                </div>-->
            <!--                <p>{data.instructions[instructionIndex]}</p>-->
            <!--            </div>-->
        </div>
    </div>
</div>
<div class="justify-center w-[auto]" style="position:absolute;left: 18px; right: 18px; bottom: 20px; z-index: 1000; background: white;">
    <hr style="margin-bottom: 20px;">
    {#if data.instructions.length > 0}
        <div style="margin-bottom: 12px; gap: 8px; display: inline-flex; flex-direction: column;">
            <p>Instructions</p>
            <p style="font-size: 26px">{data.instructions[instructionIndex]}</p>
            <br>
            <div style="display:inline-flex; flex-direction: row; gap: 14px;">
                <button class="back-button bg-transparent text-black p-2"
                        style="border-radius: 8px; border: 1px solid black; width: fit-content;" disabled={instructionIndex === 0}
                        onclick={()=> instructionIndex--}>Back
                </button>
                <button class="next-button bg-black text-white p-2"
                        style="border-radius: 8px; border: 1px solid black; width: fit-content;" disabled={instructionIndex >= data.instructions.length - 1}
                            onclick={()=> instructionIndex++}>Next
                    </button>
            </div>
        </div>
    {/if}
    <div class="inline-flex w-[100%] gap-2" style="padding-left: 20px; padding-right: 20px;">
        <form method="post" class="items-start w-[100%] gap-6" use:enhance
              onsubmit={handleSubmit}>
            <input type="hidden" name="x" bind:value={fireXCoords}>
            <input type="hidden" name="y" bind:value={fireYCoords}>
            <input type="text" class="input text-lg w-full text-center" name="description" bind:value={fireDescription}
                   placeholder="Eg. It is an electrical fire with casualties including one burned and inhaling smoke.">
        </form>
        <button class="text-5xl text-align-top h-10" onclick={startFire}>🔥</button>
    </div>
</div>


<style>
    #map {
        background-color: white;
    }

    .next-button:disabled, .back-button:disabled {
        background: lightgray;
    }
</style>