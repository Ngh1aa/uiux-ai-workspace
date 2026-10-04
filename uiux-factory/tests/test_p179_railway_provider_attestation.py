from __future__ import annotations

from types import SimpleNamespace

import core.runtime.flow_os.provider_attestation as provider_module
from core.runtime.flow_os.provider_attestation import (
    ProviderAttestationResult,
    RailwayProviderAttestor,
    resolve_canonical_integration_truth,
)


def _schema_service_source() -> dict:
    return {
        "data": {
            "__type": {
                "fields": [
                    {
                        "name": "source",
                        "type": {
                            "kind": "OBJECT",
                            "name": "ServiceSource",
                            "ofType": None,
                        },
                    }
                ]
            }
        }
    }


def _schema_source_fields() -> dict:
    return {
        "data": {
            "__type": {
                "fields": [
                    {"name": "repo"},
                    {"name": "branch"},
                ]
            }
        }
    }


def test_p179_missing_credential_remains_unknown() -> None:
    result = RailwayProviderAttestor(None).attest_repository("Ngh1aa/Nova")

    assert result.state == "unknown"
    assert result.inspection_complete is False
    assert result.credential_configured is False


def test_p179_schema_drift_fails_closed() -> None:
    def request(query: str, variables: dict):
        assert "P179ServiceSchema" in query
        return {"data": {"__type": {"fields": [{"name": "id", "type": {"kind": "SCALAR", "name": "String"}}]}}}

    result = RailwayProviderAttestor("token", request_graphql=request).attest_repository("Ngh1aa/Nova")

    assert result.state == "unknown"
    assert result.inspection_complete is False
    assert result.credential_configured is True
    assert "schema" in result.reason.lower()


def test_p179_positive_service_repo_linkage_is_configured() -> None:
    calls: list[tuple[str, dict]] = []

    def request(query: str, variables: dict):
        calls.append((query, variables))
        if "P179ServiceSchema" in query:
            return _schema_service_source()
        if "P179SourceSchema" in query:
            assert variables == {"name": "ServiceSource"}
            return _schema_source_fields()
        if "P179Projects" in query:
            return {
                "data": {
                    "projects": {
                        "edges": [{"node": {"id": "project_1", "name": "Nova"}}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        if "P179ProjectServices" in query:
            assert variables["id"] == "project_1"
            return {
                "data": {
                    "project": {
                        "id": "project_1",
                        "name": "Nova",
                        "services": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "service_1",
                                        "name": "web",
                                        "source": {
                                            "repo": "Ngh1aa/Nova",
                                            "branch": "main",
                                        },
                                    }
                                }
                            ],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        },
                    }
                }
            }
        raise AssertionError(query)

    result = RailwayProviderAttestor("token", request_graphql=request).attest_repository("Ngh1aa/Nova")

    assert result.state == "configured"
    assert result.inspection_complete is True
    assert result.credential_configured is True
    assert result.project_id == "project_1"
    assert result.project_name == "Nova"
    assert result.linked_repository == "ngh1aa/nova"
    assert result.production_branch == "main"
    assert result.connection_active is True
    assert result.evidence[0].provider == "railway"
    assert result.evidence[0].source == "provider-attestation:railway"
    assert all("mutation" not in query.lower() for query, _ in calls)


def test_p179_complete_empty_project_scope_can_prove_absence() -> None:
    def request(query: str, variables: dict):
        if "P179ServiceSchema" in query:
            return _schema_service_source()
        if "P179SourceSchema" in query:
            return _schema_source_fields()
        if "P179Projects" in query:
            return {
                "data": {
                    "projects": {
                        "edges": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        raise AssertionError(query)

    result = RailwayProviderAttestor("token", request_graphql=request).attest_repository("Ngh1aa/Nova")

    assert result.state == "not_configured"
    assert result.inspection_complete is True
    assert result.connection_active is False


def test_p179_incomplete_pagination_never_proves_absence() -> None:
    def request(query: str, variables: dict):
        if "P179ServiceSchema" in query:
            return _schema_service_source()
        if "P179SourceSchema" in query:
            return _schema_source_fields()
        if "P179Projects" in query:
            return {
                "data": {
                    "projects": {
                        "edges": [],
                        "pageInfo": {"hasNextPage": True, "endCursor": "same"},
                    }
                }
            }
        raise AssertionError(query)

    result = RailwayProviderAttestor(
        "token",
        max_pages=2,
        request_graphql=request,
    ).attest_repository("Ngh1aa/Nova")

    assert result.state == "unknown"
    assert result.inspection_complete is False


def test_p179_railway_attestation_can_be_canonical_configured_truth(monkeypatch) -> None:
    policy = SimpleNamespace(
        repository="Ngh1aa/RailwayApp",
        registered=True,
        known_integration_providers=("railway",),
    )
    monkeypatch.setattr(provider_module, "resolve_repository_policy", lambda repository: policy)

    attestation = ProviderAttestationResult(
        version="1.0",
        provider="railway",
        repository="Ngh1aa/RailwayApp",
        inspection_complete=True,
        credential_configured=True,
        state="configured",
        project_id="project_1",
        linked_repository="ngh1aa/railwayapp",
        connection_active=True,
        evidence=(),
        reason="configured",
    )

    truth = resolve_canonical_integration_truth(
        "Ngh1aa/RailwayApp",
        (),
        attestations={"railway": attestation},
        inspection_complete=True,
        inspection_channels=("repository-static", "github-provider-native", "provider-attestation"),
    )

    assert truth.passed is True
    assert truth.status == "IN_SYNC"
    assert truth.providers[0].state == "CONFIGURED_ATTESTED"
