import * as fs from 'fs';
import * as path from 'path';

export const listFilesInDirectoryWithExtension = (inputPath: string, extension: string): string[] => {
    
    const stat = fs.lstatSync(inputPath);

    const filesInDir: string[] = [];

    if (stat.isDirectory()) {
        // Handle directory conversion
        const files = fs.readdirSync(inputPath);
        const filteredFiles = files.filter(file => path.extname(file).toLowerCase() === extension.toLowerCase());

        if (filteredFiles.length === 0) {
            throw new Error(`No ${extension.toUpperCase()} files found in the selected directory`);
        }

        filesInDir.push(...filteredFiles.map(file => path.join(inputPath, file)));
    } else if (stat.isFile()) {
        // Handle single file conversion
        if (path.extname(inputPath).toLowerCase() !== extension.toLowerCase()) {
            throw new Error(`Selected file is not a ${extension.toUpperCase()} file`);
        }
        filesInDir.push(inputPath);
    } else {
        throw new Error('Selected path is neither a file nor a directory');
    }
    return filesInDir;
}


export const generateOutputPath = (inputPath: string, postfix: string, extension: string | undefined): string => {
    const parsedPath = path.parse(inputPath);
    const outputFormat = extension ? extension : parsedPath.ext.slice(1); // Use provided format or keep original
    const outputFileName = `${parsedPath.name}_${postfix}.${outputFormat}`;
    return path.join(parsedPath.dir, outputFileName);
};
