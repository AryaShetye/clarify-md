"""Google-first integration stubs for CLARIFY.MD.

These components are **not** required for the core demo and do not
introduce any billing dependency. They exist to make the architecture
"Vertex/Drive-ready" while keeping a fully local fallback.

Design principles:
- Abstract: CLARIFY.MD depends on interfaces, not concrete Google SDKs.
- Optional: No imports from `google.cloud` or Vertex SDKs in the core path.
- Documented: Each stub explains how a real integration would plug in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Protocol, runtime_checkable


# ---------------------------------
# Vertex AI Search – conceptual API
# ---------------------------------

@runtime_checkable
class MedicalKnowledgeSearch(Protocol):
    """Abstract interface for medical knowledge retrieval.

    Current implementation: uses the local ontology from
    `gemini_config.get_medical_ontology()` (fully offline, free).

    Future implementation: a Vertex AI Search index over clinical
    ontologies / FHIR resources can implement this protocol and be
    injected into agents without changing their public APIs.
    """

    def search(self, query: str, category: str, k: int = 5) -> List[str]:  # pragma: no cover - interface
        ...


@dataclass
class LocalOntologySearch:
    """Default, offline implementation backed by the local ontology.

    This is what agents currently use indirectly via `use_rag()` in
    `BaseAgent`. It demonstrates the **shape** of the future Vertex AI
    Search client without requiring cloud resources.
    """

    ontology: Dict[str, Dict[str, List[str]]]

    def search(self, query: str, category: str, k: int = 5) -> List[str]:  # pragma: no cover - thin wrapper
        query_lower = (query or "").lower()
        if category not in self.ontology:
            return []
        matches: List[str] = []
        for key, values in self.ontology[category].items():
            if any(term in query_lower for term in key.split("/")):
                matches.extend(values)
        return matches[:k]


class VertexAISearchClient:
    """Stub for a Vertex AI Search-backed implementation.

    How this would be wired in production (conceptual only):
    - Create a Vertex AI Search data store with medical ontology data.
    - Implement `search()` using the Vertex AI Search Python SDK.
    - Inject an instance into agents (or into `get_medical_ontology`)
      without changing agent method signatures.
    """

    def __init__(self, project_id: str, location: str, data_store_id: str):  # pragma: no cover - stub
        self.project_id = project_id
        self.location = location
        self.data_store_id = data_store_id

    def search(self, query: str, category: str, k: int = 5) -> List[str]:  # pragma: no cover - stub
        raise NotImplementedError(
            "Integrate with google.cloud.discoveryengine / Vertex AI Search client "
            "in a production setting. This project ships with a local fallback "
            "and does not require any paid Google Cloud resources."
        )


# -------------------------------------
# Google Drive / Colab dataset ingestion
# -------------------------------------

@runtime_checkable
class DatasetIngestion(Protocol):
    """Abstract interface for loading training/evaluation datasets.

    Current usage:
    - Local JSON/CSV files in `data/` (e.g., `clarify_md_dataset.json`).

    Future usage:
    - Google Drive / Colab notebooks can mount Drive and implement
      this interface to stream labeled narratives into training scripts
      in `training/` without changing those scripts.
    """

    def load(self, source: str) -> Any:  # pragma: no cover - interface
        ...


class LocalFileDatasetIngestion:
    """Default implementation: load datasets from local disk.

    This keeps the project fully local and hackathon-friendly.
    """

    def load(self, source: str) -> Any:  # pragma: no cover - thin wrapper
        import json
        from pathlib import Path

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {source}")

        if path.suffix.lower() in {".json"}:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        elif path.suffix.lower() in {".csv"}:
            import csv

            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            raise ValueError(f"Unsupported dataset format: {path.suffix}")


class GoogleDriveDatasetIngestion:
    """Stub for Google Drive-based dataset ingestion.

    In a Colab/Vertex AI Workbench setting, this could:
    - Mount Google Drive
    - Read CSV/JSON from a shared folder
    - Return the same Python structures as LocalFileDatasetIngestion

    The training code in `training/*.py` would depend only on the
    `DatasetIngestion` protocol, not on Drive-specific APIs.
    """

    def load(self, source: str) -> Any:  # pragma: no cover - stub
        raise NotImplementedError(
            "Use Google Colab/Drive APIs in a notebook context to implement "
            "this method. The core CLARIFY.MD project stays local by default."
        )
