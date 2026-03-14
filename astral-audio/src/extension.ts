// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as path from 'path';
import * as vscode from 'vscode';

import { AudioConverter, ConvertOptions } from './converter';
import * as dialog from './dialog';
import { TimeStretcher, TimeStretchOptions } from './timestretch';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	
	// Register command for converting to MP3 with default settings
    let convertToMp3Command = vscode.commands.registerCommand('astral-audio.convertWavToMp3', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('No file selected');
            return;
        }

        try {
            const options = await showConvertDialog();
            if (!options) {
                return; // User cancelled
            }

            const audioConverter = new AudioConverter();

            const outputPath = await audioConverter.convertToMp3(uri.fsPath, options);
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
            const options = await showConvertDialog();
            if (!options) {
                return; // User cancelled
            }

            const audioConverter = new AudioConverter();

            await audioConverter.convertToMp3(uri.fsPath, options);

            vscode.window.showInformationMessage(`Directory converted successfully`);
        } catch (error) {
            vscode.window.showErrorMessage(`Conversion failed: ${error}`);
        }
    });

    let timestretchCommand = vscode.commands.registerCommand('astral-audio.timeStretch', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('No file selected');
            return;
        }

        try {
            const options = await showTimeStretchDialog();
            if (!options) {
                return; // User cancelled
            }

            const timeStretcher = new TimeStretcher();

            const outputPath = await timeStretcher.timeStretch(uri.fsPath, options);
            vscode.window.showInformationMessage(`File time-stretched successfully: ${outputPath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Time-stretching failed: ${error}`);
        }
    });

	context.subscriptions.push(convertToMp3Command, convertDirToMp3Command, timestretchCommand);
	
}

async function showConvertDialog(): Promise<ConvertOptions | undefined> {
  
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
        sampleRate,
    };
}

interface TestDialogResult {
	name: string;
}


async function showTimeStretchDialog(): Promise<TimeStretchOptions | undefined> {
  
    const testDir = path.resolve(__dirname, './dialogs');
	const d = new dialog.WebviewDialog<TestDialogResult>(
		'webview-dialog-test', testDir, 'timestretch.html');
	const result: TestDialogResult | null = await d.getResult();

	if (result) {
		vscode.window.showInformationMessage(
			"Webview dialog result: " + JSON.stringify(result));
	} else {
		vscode.window.showInformationMessage(
			"The webview dialog was cancelled.");
	}

    return {
        target_tempo: 120, // Placeholder value, replace with actual user input from dialog
        min_rate: undefined,
        max_rate: undefined,
    };
}



// This method is called when your extension is deactivated
export function deactivate() {}
