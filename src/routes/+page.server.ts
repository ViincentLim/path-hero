import { saveResponseToFile } from '$lib/utils/saveResponse'
import { redirect } from '@sveltejs/kit';

export const actions = {
  default: async ({ request }) => {
    const formData = await request.formData();
    const name = formData.get("name");
    const file = formData.get("file");

    // Validate inputs
    if (!name || !file ) {
      return { error: "All fields are required." };
    }

    const apiUrl = `http://localhost:4000/recommendations?name=${name}&file=${file}`

    // Fetch data from the backend
    const response = await fetch(apiUrl);

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json()
    await saveResponseToFile(data, "floordata.json")

    redirect(303, "/")
  },
}