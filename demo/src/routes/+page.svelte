<script lang="ts">
    import * as Resizable from "$lib/components/ui/resizable";
    import * as Tabs from "$lib/components/ui/tabs/index.js";
    import * as Card from "$lib/components/ui/card/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import hospitalImage from '$lib/images/hospital_simple.png'

  export let data

  let taskIndex = 0
  function incrementTaskIndex() {
    if (taskIndex == data.instructions.length-1) { return }
    taskIndex = taskIndex + 1
  }

  function decrementTaskIndex() {
    if (taskIndex == 0) { return }
    taskIndex = taskIndex - 1
  }

  let questionInput = ""
  let question = "Enter question in input box below!"
  let responses = ["Waiting for questions...", "Response 1", "Response 2", "Response 3", "Response 4"]
  let responseIndex = 0

  function handleSubmitAIQuery() {
    question = questionInput
    questionInput = ""
    responseIndex = (responseIndex + 1) % responses.length
  }
</script>

<div class="w-full h-[95vh]">
    <Resizable.PaneGroup direction="horizontal" class="rounded-lg border">
    <Resizable.Pane defaultSize={70}>
        <div class="flex h-full items-center justify-center p-6">
            <img src={hospitalImage} alt="Hospital Floor" class="w-full h-full">
        </div>
    </Resizable.Pane>
    <Resizable.Handle />
    <Resizable.Pane defaultSize={25} class="flex justify-center p-3">
        <Tabs.Root value="instructions" class="w-[400px]">
        <Tabs.List class="grid w-full grid-cols-3">
          <Tabs.Trigger value="instructions">Instructions</Tabs.Trigger>
          <Tabs.Trigger value="monitor">Monitor</Tabs.Trigger>
          <Tabs.Trigger value="edit">Edit</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="edit">
          <Card.Root>
            <Card.Header>
              <Card.Title>Edit</Card.Title>
              <Card.Description>
                Make changes to your map here. Click save when you're done.
              </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2">
              <div class="space-y-1">
                <Label for="name">Name</Label>
                <Input id="name" placeholder="eg. CO2 extinguisher" />
              </div>
              <div class="space-y-1">
                <Label for="coordinates">Coordinates</Label>
                <!-- Maybe add coord markers on map? -->
                <Input id="coordinates" placeholder="X coordinates" />
                <Input id="coordinates" placeholder="Y coordinates" />
                <p class="text-sm italic">*or click on map to add item</p>
              </div>
            </Card.Content>
            <Card.Footer class="flex gap-2">
              <Button variant="secondary">Reset</Button>
              <Button>Save changes</Button>
            </Card.Footer>
          </Card.Root>
        </Tabs.Content>
        <Tabs.Content value="instructions" class="h-full">
          <Card.Root class="h-[40%] mb-3">
            <Card.Header>
              <Card.Title>Instructions</Card.Title>
              <Card.Description>
                Steps for evacuating civilians and fighting the fire.
              </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2 h-2/3">
              <div class="h-2/3">
                <h1>Task</h1>
                <p>{data.instructions[taskIndex]}</p>
              </div>
              <div class="h-1/3">
                <h1>Route</h1>
                <p>{JSON.stringify(data.routes[taskIndex])}</p>
              </div>
            </Card.Content>
            <Card.Footer class="flex gap-2">
              <Button onclick={decrementTaskIndex} variant="secondary" disabled={taskIndex==0}>Back</Button>
              <Button onclick={incrementTaskIndex} disabled={taskIndex==data.instructions.length-1}>Next</Button>
            </Card.Footer>
          </Card.Root>

          <Card.Root class="h-[53%]">
            <Card.Header>
              <Card.Title>Chat</Card.Title>
              <Card.Description>
                Ask assistant for help in real time!
              </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2 h-2/3">
              <div class="h-1/3">
                <h1 class="bold">Question</h1>
                <p>{question}</p>
              </div>
              <div class="h-2/3">
                <h1 class="bold">Response</h1>
                <p>{responses[responseIndex]}</p>
              </div>
            </Card.Content>
            <Card.Footer class="flex gap-2">
              <Input bind:value={questionInput} />
              <Button onclick={handleSubmitAIQuery}>Submit</Button>
            </Card.Footer>
          </Card.Root>
        </Tabs.Content>


        <Tabs.Content value="monitor" class="h-full">
          <Card.Root class="h-[33%] mb-3">
            <Card.Header>
              <Card.Title>Analysis</Card.Title>
              <Card.Description>
                Path Buddy's Recommendations
              </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2 h-2/3">
              <div class="h-1/2">
                <h1 class="bold">Compliance</h1>
                <p>Compliance recommendation here</p>
              </div>
              <div class="h-1/2">
                <h1 class="bold">Metrics</h1>
                <p>No. of People: 142</p>
              </div>
            </Card.Content>
          </Card.Root>
          <Card.Root class="h-[53%]">
            <Card.Header>
              <Card.Title>Live Feed</Card.Title>
              <Card.Description>
                Click room to view feed
              </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2 h-2/3">
              
            </Card.Content>
          </Card.Root>
        </Tabs.Content>
      </Tabs.Root>
    </Resizable.Pane>
    </Resizable.PaneGroup>
      
</div>