from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import typer
import tomllib

try:  # optional dependency
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
except Exception:  # pragma: no cover - optional
    OpenAIEmbeddings = None
    Chroma = None


@dataclass
class Config:
    """Configuration for the bobbing CLI."""

    openai_api_key: Optional[str] = None
    db_dir: str = "chroma"


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from ``bobbing.toml`` or ``bobbingconfig.toml``."""
    candidates: List[Path] = []
    if path:
        candidates.append(Path(path))
    else:
        for name in ("bobbing.toml", "bobbingconfig.toml"):
            candidates.append(Path.cwd() / name)
            candidates.append(Path.home() / name)
    data: dict = {}
    for candidate in candidates:
        if candidate.is_file():
            with open(candidate, "rb") as fh:
                data = tomllib.load(fh)
            break
    cfg = data.get("bobbing", data) if data else {}
    return Config(
        openai_api_key=cfg.get("openai_api_key"),
        db_dir=cfg.get("db_dir", "chroma"),
    )


def _ensure_deps() -> None:
    if not Chroma or not OpenAIEmbeddings:
        typer.echo(
            "Chroma and LangChain are required. Install project dependencies.",
            err=True,
        )
        raise typer.Exit(1)


def _init_store(cfg: Config):
    _ensure_deps()
    embeddings = OpenAIEmbeddings(openai_api_key=cfg.openai_api_key)
    return Chroma(persist_directory=cfg.db_dir, embedding_function=embeddings)


app = typer.Typer(help="Admin utility for Bob")
vectordb_app = typer.Typer(help="Manage vector databases")
app.add_typer(vectordb_app, name="vectordb")


@vectordb_app.command()
def create(
    db_dir: Optional[str] = typer.Option(None, help="Directory for the database"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file"),
) -> None:
    """Create a new Chroma vector database."""
    cfg = load_config(config)
    if db_dir:
        cfg.db_dir = db_dir
    store = _init_store(cfg)
    store.persist()
    typer.echo(f"Vector database created at {cfg.db_dir}")


@vectordb_app.command()
def view(
    db_dir: Optional[str] = typer.Option(None, help="Directory for the database"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file"),
) -> None:
    """Display basic information about the vector database."""
    cfg = load_config(config)
    if db_dir:
        cfg.db_dir = db_dir
    store = _init_store(cfg)
    try:
        count = store._collection.count()  # type: ignore[attr-defined]
    except Exception:
        count = 0
    typer.echo(f"Vector database at {cfg.db_dir} contains {count} documents")


@vectordb_app.command()
def add(
    files: List[Path] = typer.Argument(..., help="Files to embed"),
    db_dir: Optional[str] = typer.Option(None, help="Directory for the database"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file"),
) -> None:
    """Add documents to the vector database."""
    cfg = load_config(config)
    if db_dir:
        cfg.db_dir = db_dir
    store = _init_store(cfg)
    texts = [Path(p).read_text() for p in files]
    store.add_texts(texts)
    store.persist()
    typer.echo(f"Added {len(texts)} documents to {cfg.db_dir}")


@vectordb_app.command()
def remove(
    ids: List[str] = typer.Argument(..., help="Document IDs to remove"),
    db_dir: Optional[str] = typer.Option(None, help="Directory for the database"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file"),
) -> None:
    """Remove documents from the vector database by their IDs."""
    cfg = load_config(config)
    if db_dir:
        cfg.db_dir = db_dir
    store = _init_store(cfg)
    store.delete(ids)
    store.persist()
    typer.echo(f"Removed {len(ids)} documents from {cfg.db_dir}")
