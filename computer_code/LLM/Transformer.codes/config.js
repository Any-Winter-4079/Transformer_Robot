import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const otherPostsPath = "./posts/";
let otherPostsMenu = [];
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const directoryPath = path.join(__dirname, 'hierarchies');

async function loadData() {
    try {
        const files = await fs.promises.readdir(directoryPath);
        const filteredFiles = files.filter(file => path.extname(file) === '.json')
                                   .sort((a, b) => parseInt(a.match(/\d+/), 10) - parseInt(b.match(/\d+/), 10));

        const readFilePromises = filteredFiles.map(file => {
            const filePath = path.join(directoryPath, file);
            return fs.promises.readFile(filePath, 'utf8').then(JSON.parse);
        });

        otherPostsMenu = await Promise.all(readFilePromises);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

await loadData();

export { otherPostsMenu, otherPostsPath };
