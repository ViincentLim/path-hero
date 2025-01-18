import { saveResponseToFile } from '$lib/utils/saveResponse'
import { readFile } from 'fs/promises'
// @ts-ignore
import path from 'path'

export async function load() {
  const floorDataFilePath = path.resolve('./src/lib/floordata.json')
  const fireDataFilePath = path.resolve('./src/lib/firedata.json')

  try {
    // FLOOR DATA
    const floorDataFileData = await readFile(floorDataFilePath, 'utf-8');
    const floorData = JSON.parse(floorDataFileData)
    const extinguishers = floorData.fire_extinguishers
    const exits = floorData.exits
    const height = floorData.height
    const width = floorData.width
    const rooms = floorData.rooms

    // FIRE DATA
    const fireDataFileData = await readFile(fireDataFilePath, 'utf-8')
    const fireData = JSON.parse(fireDataFileData)
    const recommendations = fireData.recommendations
    const instructions = recommendations.instructions
    const routes = recommendations.routes

    return { 
      height,
      width,
      rooms,
      extinguishers,
      exits, 
      instructions,
      routes,
    }
  } catch (error) {
    console.error('Error reading recommendations file:', error);
    return { 
        analysis: null,
        spreadData: null,
        volumeData: null,
        xAxis: null,
    }
  }
}


export const actions = {
 default: async ({ request }: { request: Request }) => {
   const formData = await request.formData();
   const x = formData.get("x")
   const y = formData.get("y")
   const description = formData.get("description")
   const xArr = (x! as string).split(",")
   const yArr = (y! as string).split(",")
   const coords = []
   for (let i = 0; i < xArr.length-1; i++) {
    coords.push([xArr[i], yArr[i]])
   }

   // Validate inputs
   if (!x || !y ) {
     return { error: "All fields are required." };
   }


   const requestBody = JSON.stringify({
     coords: coords,
     description: description,
   })
   console.log(requestBody)

   const apiUrl = `http://localhost:8000/api/fire`

   // Fetch data from the backend
  //  const response = await fetch(apiUrl, {
  //    method: "POST",
  //    headers: {
  //      "Content-Type": "application/json", // Set content type to JSON
  //    },
  //    body: requestBody,
  //  })


  //  if (!response.ok) {
  //    throw new Error(`API request failed with status ${response.status}`);
  //  }


  //  const data = await response.json()
  //  await saveResponseToFile(data, "firedata.json")
 },
}
