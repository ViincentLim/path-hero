import { writeFile } from 'fs/promises';
import path from 'path';

export async function saveResponseToFile(response: object, fileName: string) {
  const filePath = path.resolve('./src/lib', fileName);

  try {
    await writeFile(filePath, JSON.stringify(response, null, 2), 'utf-8');
    console.log(`Response saved to ${filePath}`);
  } catch (error) {
    console.error('Error saving response to file:', error);
  }
}