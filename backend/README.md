# Music Production Client Backend

The backend can be called through 2 APIs:
1. through the `cli`
2. through REST endpoints


## Use the REST endpoints

You have to start the server:

```sh
fastapi dev src/mpcli/api.py
```

The best way to use the REST endpoints is to use a REST Client. The directory [bruno-api](../bruno-api/) provides a pre-packaged configuration.

## Use the CLI

You don't need to run the frontend to run the CLI, but the drawback is that you have to configure things in the file `config.toml`

A configuration template is provided [here](./cli-config-template.toml)

* `poetry run timestretch` will timestrech the given files to the target tempo (`target_tempo`)
* `poetry run detect_tempo` will just give the tempos of the files located in the source directory 
* `poetry run convert` 
* `poetry run normalize` 
