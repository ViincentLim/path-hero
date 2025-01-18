<script lang="ts">
    let name: string
    let file: string
  </script>
  
  <nav class="flex p-2 gap-4">
    <a href="/" class="pl-4 pt-2">&#10094;</a>
  </nav>
  <div class="flex flex-col items-center p-10">
      <h2 class="text-4xl mb-10">ADD FLOORPLAN</h2>
      <form method="post" class="flex flex-col gap-5 w-1/3 text-xl items-center p-5 mb-10">
        <label class="w-full flex justify-between">
          <p class="flex items-center text-xl">
            Floor Name
          </p>
          <input type="text" class="input w-2/3" name="name" bind:value={name} placeholder="e.g. Block B, Level 5" required />
        </label> 
        
        <label class="w-full flex justify-between mb-4">
        <p class="flex items-center text-xl">
            Image File
        </p>
        <input type="file" class="input w-2/3 text-sm text-gray-400" name="file" bind:value={file}>
        </label>
        
          <button class="btn  text-lg variant-ghost-primary" type="submit">Submit</button>
        </form>
  </div>