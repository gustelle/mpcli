// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

import { AudioConverter } from './audioConverter';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const audioConverter = new AudioConverter();

	// Register command for converting to MP3 with default settings
    let convertToMp3Command = vscode.commands.registerCommand('astral-audio.convertWavToMp3', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('No file selected');
            return;
        }

        try {
            const options = await showConversionOptionsDialog();
            if (!options) {
                return; // User cancelled
            }

            const outputPath = await audioConverter.convertToMp3(uri.fsPath, {
                sampleRate: options.sampleRate,
            });
            vscode.window.showInformationMessage(`File converted successfully: ${outputPath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Conversion failed: ${error}`);
        }
    });


    let convertDirToMp3Command = vscode.commands.registerCommand('astral-audio.convertDirToMp3', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('No directory selected');
            return;
        }

        try {
            const options = await showConversionOptionsDialog();
            if (!options) {
                return; // User cancelled
            }

            await audioConverter.convertToMp3(uri.fsPath, {
                sampleRate: options.sampleRate,
            });

            vscode.window.showInformationMessage(`Directory converted successfully`);
        } catch (error) {
            vscode.window.showErrorMessage(`Conversion failed: ${error}`);
        }
    });

	context.subscriptions.push(convertToMp3Command, convertDirToMp3Command);
	
}

async function showConversionOptionsDialog(): Promise<ConversionOptions | undefined> {
  
    // Sample rate selection - allow custom input
    const sampleRateInput = await vscode.window.showInputBox({
        prompt: 'Enter sample rate in Hz (e.g., 44100, 48000, 96000)',
        value: '44100',
        validateInput: (value) => {
            const num = parseInt(value);
            if (isNaN(num) || num < 8000 || num > 192000) {
                return 'Please enter a valid sample rate between 8000 and 192000 Hz';
            }
            return null;
        }
    });
    if (!sampleRateInput) {return undefined;}
    const sampleRate = parseInt(sampleRateInput);

    return {
        format: 'mp3',
        sampleRate,
    };
}

interface ConversionOptions {
    format: 'wav' | 'mp3';
    sampleRate: number;
}


// This method is called when your extension is deactivated
export function deactivate() {}
