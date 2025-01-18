import { saveResponseToFile } from '$lib/utils/saveResponse'
import { readFile } from 'fs/promises'
// @ts-ignore
import path from 'path'
import { promises as fs } from 'fs';

async function fileExists(filePath: string) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

export async function load() {
  const floorDataFilePath = path.resolve('./src/lib/floordata.json')
  const fireDataFilePath = path.resolve('./src/lib/firedata.json')

  let height, width, rooms, extinguisherPowder, extinguisherCo2, extinguisherFoam, hoseReel, exits;
  let instructions = [], routes = [];

    // FLOOR DATA
    if (await fileExists(floorDataFilePath)) {
      try {
        const floorDataFileData = await fs.readFile(floorDataFilePath, 'utf-8');
        const floorData = JSON.parse(floorDataFileData);
        const icons = floorData.icons_midpoints;
        height = floorData.height;
        width = floorData.width;
        rooms = floorData.rooms;
        extinguisherPowder = transformCoordinates(icons.extinguisher_powder, height);
        extinguisherCo2 = transformCoordinates(icons.extinguisher_co2, height);
        extinguisherFoam = transformCoordinates(icons.extinguisher_foam, height);
        hoseReel = transformCoordinates(icons.hosereel, height);
        exits = transformCoordinates(icons.exit, height);
      } catch (err) {
        console.error(`Error reading or parsing floor data: ${err}`);
      }
    } else {
      console.warn(`Floor data file not found: ${floorDataFilePath}`);
    }

    // FIRE DATA
    if (await fileExists(fireDataFilePath)) {
      try {
        const fireDataFileData = await fs.readFile(fireDataFilePath, 'utf-8');
        const fireData = JSON.parse(fireDataFileData);
        const recommendations = fireData.recommendations;
        instructions = recommendations.instructions || [];
        routes = recommendations.routes || [];
      } catch (err) {
        console.error(`Error reading or parsing fire data: ${err}`);
      }
    } else {
      console.warn(`Fire data file not found: ${fireDataFilePath}`);
    }

    return {
      height,
      width,
      rooms,
      extinguisherPowder,
      extinguisherCo2,
      extinguisherFoam,
      hoseReel,
      exits,
      instructions,
      routes,
    };
  } 

function transformCoordinates(coords: number[], imageHeight: number) {
  if (!coords || !Array.isArray(coords)) {
    console.warn('Invalid or missing coordinates:', coords);
    return []
  }
  // @ts-ignore
  return coords.map(([y, x]) => [imageHeight - y, x]);
}

export const actions = {
 default: async ({ request }: { request: Request }) => {
   const formData = await request.formData();
   const x = formData.get("x")
   const y = formData.get("y")
   const description = formData.get("description")
   const xArr = (x! as string).split(",")
   const yArr = (y! as string).split(",")
   const coordinates = []
   for (let i = 0; i < xArr.length-1; i++) {
    coordinates.push([Number(xArr[i]), Number(yArr[i])])
   }

   // Validate inputs
   if (!x || !y ) {
     return { error: "All fields are required." };
   }


   const requestBody = JSON.stringify({
     coordinates: coordinates,
     description: description,
   })
   console.log(requestBody)

   const apiUrl = `http://localhost:8000/api/fire`
  // Fetch data from the backend
   const response = await fetch(apiUrl, {
     method: "POST",
     headers: {
       "Content-Type": "application/json", // Set content type to JSON
     },
     body: requestBody,
   })


   if (!response.ok) {
     throw new Error(`API request failed with status ${response.status}`);
   }


   const data = await response.json()
   await saveResponseToFile(data, "floordata.json")
 },
}
