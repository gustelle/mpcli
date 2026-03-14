import * as fs from 'fs';
import { readFile } from 'node:fs/promises';
import * as path from 'path';
import * as vscode from 'vscode';
import { generateOutputPath, listFilesInDirectoryWithExtension } from './files';

export interface TimeStretchOptions {
    target_tempo: number | undefined,
    min_rate: number | undefined,
    max_rate: number | undefined,
}


export class TimeStretcher {

    constructor() {}

    private async doTimeStretchFile(
        token: vscode.CancellationToken, 
        progress: vscode.Progress<{ message?: string; increment?: number }>,
        inputPath: string, 
        options: TimeStretchOptions): Promise<string> {

        const outputPath = generateOutputPath(inputPath, 'timestretched', undefined);

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
                formData.append('target_tempo', options.target_tempo?.toString() || '');
                formData.append('min_rate', options.min_rate?.toString() || '');
                formData.append('max_rate', options.max_rate?.toString() || '');
                
                const requestOptions: RequestInit = {
                    method: 'POST',
                    body: formData
                };

                fetch('http://localhost:8000/timestretch', requestOptions)
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
     * @param options The options for time-stretching
     * @returns The path to the time-stretched audio file
     */
    public async timeStretch(inputPath: string, options: TimeStretchOptions): Promise<string> {
        
        // Validate input file exists
        if (!fs.existsSync(inputPath)) {
            throw new Error(`Input file does not exist: ${inputPath}`);
        }

        const filesToConvert: string[] = listFilesInDirectoryWithExtension(inputPath, '.wav');

        return vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Time-stretching audio...",
            cancellable: true
        }, async (progress, cancellationToken) => {

            const promises = filesToConvert.map(file => this.doTimeStretchFile(cancellationToken, progress, file, options));

            return Promise.all(promises).then(outputPaths => {
                // Handle successful conversion of all files
                console.log('All files time-stretched successfully:', outputPaths);
                return 'Time-stretching complete';
             }).catch(err => {
                // Handle errors during conversion
                throw new Error(`Time-stretching failed: ${err.message}`);
             });
            
            
        });
    }


}
