from fastapi.testclient import TestClient
from aegis.main import app

def test_strict_state_machine_transition_rejections():
    # 'with TestClient(app)' guarantees the lifespan event runs and seeds the moderator user
    with TestClient(app) as client:
        # 1. Authenticate as moderator
        auth_res = client.post("/api/v1/moderator/auth/token", json={
            "username": "gdg_moderator",
            "password": "Aegis@SRM2026!"
        })
        assert auth_res.status_code == 200
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Submit anonymous report
        submit_res = client.post("/api/v1/escrow/submit", json={
            "category": "Corruption",
            "description": "Deliberate financial manipulation detected in departmental procurement."
        })
        assert submit_res.status_code == 201
        case_token = submit_res.json()["claim_token"]

        # 3. Invalid jump: SUBMITTED directly to RESOLVED must fail with HTTP 409
        bad_transition = client.patch(
            f"/api/v1/moderator/reports/{case_token}/transition",
            headers=headers,
            json={"new_status": "RESOLVED", "resolution_note": "Skipping review"}
        )
        assert bad_transition.status_code == 409

        # 4. Valid transition: SUBMITTED -> UNDER_REVIEW must succeed
        valid_step1 = client.patch(
            f"/api/v1/moderator/reports/{case_token}/transition",
            headers=headers,
            json={"new_status": "UNDER_REVIEW", "resolution_note": "Assigned to committee"}
        )
        assert valid_step1.status_code == 200
        assert valid_step1.json()["status"] == "UNDER_REVIEW"