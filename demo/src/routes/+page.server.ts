import path from 'path'
import fs from 'fs/promises'

export async function load() {
    const fireDataFilePath = path.resolve('../src/lib/firedata.json')
    const fireDataFileData = await fs.readFile(fireDataFilePath, "utf-8")
    const fireData = JSON.parse(fireDataFileData)
    const instructions = fireData.instructions || []
    const routes = fireData.instruction_paths || []

    return {
        instructions,
        routes
    }
}