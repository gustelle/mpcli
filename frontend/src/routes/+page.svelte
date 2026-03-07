<script lang="ts">
	import { FileIcon } from '@lucide/svelte';
	import { FileUpload } from '@skeletonlabs/skeleton-svelte';
	const maxFiles = 5;
	const acceptedMimeTypes = [
		'audio/wav',
		'audio/x-wav',
		'audio/vnd.wave',
		'audio/wave',
		'audio/mp3',
		'audio/mpeg',
	]

	type TempoResponse = {
		tempo: number;
		source_format: string;
		source_name: string;
	}

	async function getTempo(file : File) : Promise<TempoResponse> {
		try {
			let formData = new FormData();
			formData.append("file", file);
			const response = await fetch('http://localhost:8000/tempo', {
				method: 'POST',
				body: formData,
			});

			// format tempo on the backend to 2 decimal places
			const tempoResponse = await response.json();
			tempoResponse.tempo = parseFloat(tempoResponse.tempo.toFixed(2));
			return tempoResponse;
		} catch (error) {
			console.error(error);
			return Promise.reject(error);
		}
		
	}

</script>

<FileUpload maxFiles={maxFiles} accept={acceptedMimeTypes.join(',')}>
	<FileUpload.Label>Upload Audio Files</FileUpload.Label>
	<FileUpload.Dropzone>
		<FileIcon class="size-10" />
		<span>Select file or drag here.</span>
		<FileUpload.Trigger>Browse Files</FileUpload.Trigger>
		<FileUpload.HiddenInput />
	</FileUpload.Dropzone>
	<FileUpload.ItemGroup>
		<FileUpload.Context>
			{#snippet children(fileUpload)}
				{#each fileUpload().acceptedFiles as file (file.name)}
					{#await getTempo(file)}
						<FileUpload.Item {file}>
							<FileUpload.ItemName>{file.name}</FileUpload.ItemName>
							<FileUpload.ItemSizeText>
								Calculating tempo...
							</FileUpload.ItemSizeText>
							<FileUpload.ItemDeleteTrigger />
						</FileUpload.Item>
					{:then value }
						<FileUpload.Item {file}>
							<FileUpload.ItemName>{file.name}</FileUpload.ItemName>
							<FileUpload.ItemSizeText>
								<button type="button" class="chip preset-filled-primary-500">{value.tempo} BPM</button>
							</FileUpload.ItemSizeText>
							<FileUpload.ItemDeleteTrigger />
						</FileUpload.Item>
					{:catch error}
						<FileUpload.Item {file}>
							<FileUpload.ItemName>{file.name}</FileUpload.ItemName>
							<FileUpload.ItemSizeText>
								{error.message}
							</FileUpload.ItemSizeText>
							<FileUpload.ItemDeleteTrigger />
						</FileUpload.Item>
					{/await}
				{/each}
			{/snippet}
		</FileUpload.Context>
	</FileUpload.ItemGroup>
	<FileUpload.ClearTrigger>Clear Files</FileUpload.ClearTrigger>
</FileUpload>