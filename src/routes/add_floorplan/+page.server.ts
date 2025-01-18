import { saveResponseToFile } from '$lib/utils/saveResponse'
import { redirect } from '@sveltejs/kit';


export const actions = {
 default: async ({ request }: { request: Request }) => {
   const formData = await request.formData();
   const name = formData.get("name")
   const filename = formData.get("file")
   const requestBody = JSON.stringify({
     description: name,
     image_filename: filename
   })
   console.log(requestBody);

   // Validate inputs
   if (!name || !filename ) {
     return { error: "All fields are required." };
   }

   const apiUrl = `http://localhost:8000/api/floorplan`

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


   redirect(303, "/")
 },
}
