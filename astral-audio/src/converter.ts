

import * as fs from 'fs';
import { readFile } from 'node:fs/promises';
import * as path from 'path';
import * as vscode from 'vscode';
import { generateOutputPath, listFilesInDirectoryWithExtension } from './files';

export interface ConvertOptions {
    sampleRate: number;
}


export class AudioConverter {

    constructor() {
        // TODO: Initialize any necessary resources or configurations for the converter
    }


    private async doConvertFile(
        token: vscode.CancellationToken, 
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        inputPath: string, 
        options: ConvertOptions): Promise<string> {

        const outputPath = generateOutputPath(inputPath, 'converted', 'mp3');

        return new Promise<string>((resolve, reject) => {

            // Handle cancellation
            token.onCancellationRequested(() => {
                // command.kill('SIGKILL');
                reject(new Error('Conversion was cancelled by user'));
            });
            
            readFile(inputPath).then(buffer => {

                progress.report({ increment: 10, message: `sending file ${path.basename(inputPath)}` });
                
                const formData = new FormData();
                formData.append('file', new Blob([buffer]), path.basename(inputPath));
                formData.append('target_format', 'mp3');
                formData.append('sample_rate', options.sampleRate.toString());
                
                const requestOptions: RequestInit = {
                    method: 'POST',
                    body: formData
                };

                fetch('http://localhost:8000/convert', requestOptions)
                    .then(response => {
                        if (!response.ok) {
                            return response.text().then(text => {
                                throw new Error(`${response.status}: ${text}`);
                            });
                        }
                        progress.report({ increment: 50, message: "receiving file..." });
                        return response.blob();
                    })
                    .then(data => {
                        // Save the converted file to the output path
                        data.arrayBuffer().then(buffer => {
                            const b = Buffer.from(buffer);
                            fs.writeFile(outputPath, b, (err) => {
                                if (err) {
                                    reject(new Error(`Failed to save converted file: ${err.message}`));
                                } else {
                                    progress.report({ increment: 100, message: "conversion complete" });
                                    resolve(outputPath);
                                }
                            });
                        });
                    })
                    .catch(err => {
                        reject(new Error(`Conversion failed: ${err.message}`));
                    });
                }
            ).catch(err => {
                reject(new Error(`Failed to read input file: ${err.message}`));
            });
        });
    }
    
    /**
     * 
     * @param inputPath The path to the input audio file
     * @param options The options for MP3 conversion
     * @returns The path to the converted MP3 file
     */
    public async convertToMp3(inputPath: string, options: ConvertOptions): Promise<string> {
        
        // Validate input file exists
        if (!fs.existsSync(inputPath)) {
            throw new Error(`Input file does not exist: ${inputPath}`);
        }

        const filesToConvert: string[] = listFilesInDirectoryWithExtension(inputPath, '.wav');

        return vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Converting to MP3...",
            cancellable: true
        }, async (progress, cancellationToken) => {

            const promises = filesToConvert.map(file => this.doConvertFile(cancellationToken, progress, file, options));

            return Promise.all(promises).then(outputPaths => {
                // Handle successful conversion of all files
                console.log('All files converted successfully:', outputPaths);
                return 'Conversion complete';
             }).catch(err => {
                // Handle errors during conversion
                throw new Error(`Conversion failed: ${err.message}`);
             });
            
            
        });
    }

    
}