import pytest

def test_email_and_sms_approved(otp_svc, mock_email, mock_sms):
    txn = "txn-appr"
    phone = "+15550001"
    email = "test@example.com"
    
    # Send both
    otp_sms = otp_svc.send_sms_otp(txn, phone)
    otp_email = otp_svc.send_email_otp(txn, email)
    
    # Verify both matched
    ok_sms, _ = otp_svc.verify_otp(txn, "sms", otp_sms)
    ok_email, _ = otp_svc.verify_otp(txn, "email", otp_email)
    
    assert ok_sms is True
    assert ok_email is True
    assert len(mock_sms) == 1
    assert len(mock_email) == 1

def test_expired_returns_timeout(otp_svc):
    ok, reason = otp_svc.verify_otp("nonexistent", "sms", "123456")
    assert ok is False
    assert reason == "expired"

def test_mismatch_returns_mismatch(otp_svc):
    txn = "txn-mis"
    otp_svc.store_otp(txn, "sms", "hashed_val") # manual store for simple test
    
    # Use real hashing to ensure mismatch works
    import hashlib
    real_otp = "111111"
    wrong_otp = "222222"
    sha = hashlib.sha256(real_otp.encode()).hexdigest()
    otp_svc.store_otp(txn, "sms", sha)
    
    ok, reason = otp_svc.verify_otp(txn, "sms", wrong_otp)
    assert ok is False
    assert reason == "mismatch"

def test_escalation_idempotent():
    from services import storage
    storage.init_db()
    
    user, txn = "user1", "txn1"
    storage.flag_account(user, txn, "mismatch")
    storage.flag_account(user, txn, "mismatch")
    
    rows = storage.get_flagged_accounts()
    # Should only have one entry due to UNIQUE constraint
    assert len(rows) == 1
