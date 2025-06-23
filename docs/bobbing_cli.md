# Bobbing CLI

The `bobbing` utility provides administrative commands for the Bob project. It
manages the local Chroma vector database used by the Bob and Tutor agents.

## Installation

Install the project in editable mode to expose the `bobbing` command:

```bash
uv pip install -e .
```

## Usage

Common commands:

```bash
bobbing vectordb create        # initialize the database
bobbing vectordb view          # show stored document count
bobbing vectordb add FILE1 ... # add and embed documents
```

Configuration is read from `bobbing.toml` or `bobbingconfig.toml` in the current
working directory or your home directory. You can also specify a file explicitly
with `--config path/to/file.toml`.
