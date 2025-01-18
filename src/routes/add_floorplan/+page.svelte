<script lang="ts">
    let name: string
    let file: string
  </script>
  
  <nav class="flex p-4 gap-4 underline">
    <a href="/" class="text-3xl">&#9756;</a>
  </nav>
  <div class="flex flex-col items-center p-10">
      <h2 class="text-4xl mb-10">ADD FLOORPLAN</h2>
      <form method="post" class="flex flex-col gap-5 w-1/2 text-xl items-center p-5 mb-10">
        <label class="w-full flex justify-between">
          <p class="flex items-center text-xl">
            Floorplan Name
          </p>
          <input type="text" class="input w-1/2 md:w-2/3" name="asset" bind:value={name} placeholder="e.g., ETF_EMB" required />
        </label> 
        
        <label class="w-full flex justify-between mb-4">
        <p class="flex items-center text-xl">
            .png File
        </p>
        <input type="file" class="input" bind:value={file}>
        </label>
        
          <button class="btn  text-lg variant-ghost-primary" type="submit">Submit</button>
        </form>
  </div>