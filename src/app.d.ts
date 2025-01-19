// See https://svelte.dev/docs/kit/types#app.d.ts

import type { LatLngExpression } from "leaflet"

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

interface Room {
	name: string
	coords: number[]
	route: number[][]
}