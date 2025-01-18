import { saveResponseToFile } from '$lib/utils/saveResponse'
import { redirect } from '@sveltejs/kit';


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
    coords.push([yArr[i], xArr[i]])
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
  //  await saveResponseToFile(data, "floordata.json")
 },
}
