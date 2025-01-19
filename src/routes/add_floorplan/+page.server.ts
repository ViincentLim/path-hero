import { saveResponseToFile } from '$lib/utils/saveResponse'
import { redirect } from '@sveltejs/kit'
import fs from 'fs/promises'
// @ts-ignore
import path from 'path'


export const actions = {
 default: async ({ request }: { request: Request }) => {
   const formData = await request.formData();
   const name = formData.get("name")
   const description = formData.get("description")
   const filename = formData.get("file")
   const requestBody = JSON.stringify({
     description: description,
     image_filename: filename
   })
   console.log(requestBody);

   // Validate inputs
   if (!name || !filename ) {
     return { error: "All fields are required." };
   }

   const apiUrl = `http://127.0.0.1:8000/api/floorplan`

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
   if (data !== null) {
      data.name = name
      data.description = description
      data.fileName = filename
     await saveResponseToFile(data, "floordata.json")
   } 

   const fireDataFilePath = path.resolve('src/lib/firedata.json');

    try {
      await fs.unlink(fireDataFilePath);
      console.log("lib/firedata.json has been deleted.")
    } catch (error) {
      if (error === 'ENOENT') {
        console.log("lib/firedata.json does not exist, skipping deletion.");
      } else {
        console.error("An error occurred while trying to delete lib/firedata.json:", error);
      }
    }


   redirect(303, "/")
 },
}
