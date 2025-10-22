# Boot-Monitoring Web Service - Security & Code Quality Improvements

**Date:** 2025-10-22
**Version:** 2.0
**Branch:** web2_branch

---

## Executive Summary

This document outlines comprehensive security and code quality improvements implemented for the Boot-Monitoring web service. The improvements address **critical security vulnerabilities**, enhance **code quality**, and establish **best practices** for future development.

### Critical Improvements Implemented

1. ✅ **Bcrypt Password Hashing** - Replaced weak SHA-256 with industry-standard bcrypt
2. ✅ **Input Validation Framework** - Comprehensive validation to prevent injection attacks
3. ✅ **Code Quality Cleanup** - Removed debug statements, added documentation
4. ✅ **Type Hints Enhancement** - Improved type safety and code clarity

---

## 1. Security Improvements

### 1.1 Password Hashing Migration (CRITICAL)

**Problem:**
- Original implementation used SHA-256 with a static salt (`"jebi_salt_2025"`)
- Vulnerable to rainbow table attacks and GPU-based cracking
- Not compliant with OWASP password storage guidelines

**Solution:**
- Implemented bcrypt with automatic salt generation (12 rounds)
- Each password gets a unique, random salt
- Computationally expensive to crack (resistant to brute force)

**Files Modified:**
- [`app/models/__init__.py`](app/models/__init__.py) - Updated `User.hash_password()` and `User.verify_password()`
- [`requirements.txt`](requirements.txt) - Added `bcrypt==4.2.1`

**Code Changes:**

```python
# OLD - VULNERABLE
@staticmethod
def hash_password(password: str) -> str:
    salt = "jebi_salt_2025"  # Static salt!
    return hashlib.sha256((password + salt).encode()).hexdigest()

# NEW - SECURE
@staticmethod
def hash_password(password: str) -> str:
    """Hash password using bcrypt with automatic salt generation."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

@staticmethod
def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False
```

**Migration Required:**
- Run [`scripts/migrate_passwords.py`](scripts/migrate_passwords.py) to update existing user passwords
- See "Migration Guide" section below

---

### 1.2 Input Validation Framework (HIGH)

**Problem:**
- No validation on device IDs, service names, or actions
- Potential for injection attacks via crafted inputs
- Path traversal vulnerabilities in file operations

**Solution:**
- Created comprehensive validation framework in [`app/utils/validators.py`](app/utils/validators.py)
- Whitelist-based validation for all critical inputs
- Centralized validation logic for consistency

**Features:**

```python
from app.utils.validators import InputValidator

# Device ID validation (against config_map_revpi)
is_valid, error = InputValidator.validate_device_id('LedProcessor')  # ✓ Valid
is_valid, error = InputValidator.validate_device_id('HackerDevice')  # ✗ Invalid

# Service name validation (whitelist)
is_valid, error = InputValidator.validate_service_name('jebi-switchboard-guard.service')  # ✓ Valid

# Action validation
is_valid, error = InputValidator.validate_device_action('on')  # ✓ Valid
is_valid, error = InputValidator.validate_device_action('hack')  # ✗ Invalid

# Filename validation (path traversal protection)
is_valid, error = InputValidator.validate_filename('logfile.log')  # ✓ Valid
is_valid, error = InputValidator.validate_filename('../../../etc/passwd')  # ✗ Invalid
```

**Validations Implemented:**
- ✅ Device IDs (whitelist from `config_map_revpi`)
- ✅ Service names (whitelist: `jebi-switchboard-guard.service`, etc.)
- ✅ Device actions (`on`, `off`, `status`)
- ✅ Service actions (`start`, `stop`, `restart`, `status`)
- ✅ Schedule days (`mon`, `tue`, `wed`, etc.)
- ✅ Time format (HH:MM, 24-hour)
- ✅ Filenames (path traversal prevention)

**Controller Integration:**
- Updated [`app/controllers/revpi_controller.py`](app/controllers/revpi_controller.py) to validate all inputs

```python
# Example: RevPi toggle endpoint
@login_required
def revpi_toggle(self):
    device_id = request.get_json().get('device')
    action_str = request.get_json().get('action')

    # Validate device ID
    is_valid, error_msg = InputValidator.validate_device_id(device_id)
    if not is_valid:
        logger.warning(f"Invalid device ID attempt: {device_id}")
        return jsonify({'success': False, 'message': error_msg}), 400

    # Validate action
    is_valid, error_msg = InputValidator.validate_device_action(action_str)
    if not is_valid:
        logger.warning(f"Invalid action attempt: {action_str}")
        return jsonify({'success': False, 'message': error_msg}), 400

    # ... proceed with validated inputs
```

---

### 1.3 Code Quality & Security Cleanup

**Removed Debug Print Statements:**

1. **[`app/services/revpi_service.py:71`](app/services/revpi_service.py#L71)**
   ```python
   # BEFORE
   print(first_line)  # Debug statement exposed in production

   # AFTER
   logger.debug(f"piTest output for {device_id}: {first_line}")
   ```

2. **[`app/services/systemd_service.py:31`](app/services/systemd_service.py#L31)**
   ```python
   # BEFORE
   print("tem,ptemp")  # Typo and debug statement

   # AFTER
   # Removed entirely
   ```

**Benefits:**
- Prevents information leakage in production
- Cleaner logs and output
- Professional code standards

---

## 2. Code Quality Improvements

### 2.1 Enhanced Type Hints & Documentation

**[`app/__init__.py`](app/__init__.py)** - Application Factory

```python
from typing import Optional

def create_app(environment: Optional[str] = None) -> Flask:
    """
    Application factory function with enhanced validation and error handling.

    Creates and configures a Flask application instance with:
    - Logging configuration
    - Database initialization
    - Security headers
    - Blueprint registration
    - Error handlers

    Args:
        environment: Environment name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV from environment or 'default'

    Returns:
        Flask: Configured Flask application instance

    Raises:
        ValueError: If configuration validation fails
        Exception: If database initialization fails
    """
```

### 2.2 Password Verification Logic Improvement

**[`app/models/__init__.py`](app/models/__init__.py)** - User Model

```python
def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials and return user data.

    Args:
        username: Username to verify
        password: Plain text password to verify

    Returns:
        Optional[Dict]: User data if authenticated, None otherwise
    """
    # Fetch user from database
    cursor.execute(
        'SELECT id, username, password_hash, created_at, last_login
         FROM users WHERE username = ? AND is_active = 1',
        (username,)
    )
    user_row = cursor.fetchone()

    if user_row:
        # Verify password using bcrypt
        if self.verify_password(password, user_row['password_hash']):
            # Update last login
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user_row['id'],)
            )
            conn.commit()

            # Return user data WITHOUT password hash
            user_data = dict(user_row)
            del user_data['password_hash']  # Security: never return hash
            return user_data

    return None
```

**Key Improvements:**
- Separates user retrieval from password verification
- Never returns password hash to caller
- Better error handling
- Comprehensive docstrings

---

## 3. Migration Guide

### 3.1 Password Migration Steps

**⚠️ CRITICAL: Run this migration before deploying the updated code!**

1. **Install bcrypt dependency:**
   ```bash
   pip install bcrypt==4.2.1
   # Or: pip install -r requirements.txt
   ```

2. **Run migration script:**
   ```bash
   python scripts/migrate_passwords.py
   ```

3. **Follow prompts:**
   - Script will create automatic backup
   - Enter plaintext password for each user
   - OR use default password from config

4. **Verify migration:**
   - Test login with each user account
   - Check that authentication works correctly

**Migration Script Features:**
- ✅ Automatic database backup (timestamped)
- ✅ Rollback on failure
- ✅ Skip users already using bcrypt
- ✅ Interactive password entry
- ✅ Option to use default password for all users

**Example Output:**
```
============================================================
Boot-Monitoring Password Migration Script
============================================================

Database: dev_users.db

Found 1 user(s) to migrate.

--- Migrating user: bradken ---
Using default password for 'bradken'
✓ Successfully migrated password for 'bradken'

============================================================
Migration completed successfully!
Migrated: 1/1 users
Backup saved to: dev_users.db.backup_20251022_143022
============================================================
```

### 3.2 Testing After Migration

1. **Test login functionality:**
   ```bash
   # Start application
   python web.py

   # Test login at http://localhost:5010/login
   # Username: bradken
   # Password: adminBradken25 (or your custom password)
   ```

2. **Verify password hash format in database:**
   ```bash
   sqlite3 dev_users.db "SELECT username, substr(password_hash, 1, 10) FROM users;"
   ```

   Expected output: `$2b$12$...` (bcrypt format)

3. **Check logs for authentication events:**
   ```bash
   tail -f logs/jebi_web.log | grep "authenticated"
   ```

---

## 4. Remaining Security Recommendations

### 4.1 High Priority (Not Yet Implemented)

#### CSRF Token Protection
**Status:** ⚠️ Security.js references CSRF tokens but they're not generated

**Recommendation:**
```bash
pip install Flask-WTF
```

```python
# In app/__init__.py
from flask_wtf.csrf import CSRFProtect

def create_app(environment=None):
    app = Flask(__name__)
    csrf = CSRFProtect(app)
    # ...
```

**Impact:** Prevents cross-site request forgery attacks on state-changing endpoints

---

#### Server-Side Session Management
**Status:** ⚠️ `user_sessions` table exists but not used

**Recommendation:**
- Implement Flask-Session with Redis backend
- Enable immediate session revocation
- Track active sessions per user

**Impact:** Better session control, supports logout from all devices

---

#### HTTPS Enforcement
**Status:** ⚠️ Application accepts HTTP connections

**Recommendation:**
```python
# In app/__init__.py
from flask_talisman import Talisman

def create_app(environment=None):
    app = Flask(__name__)
    if not app.config['DEBUG']:
        Talisman(app, force_https=True)
    # ...
```

**Impact:** Prevents session hijacking via man-in-the-middle attacks

---

### 4.2 Medium Priority

#### Content Security Policy (CSP)
**Current:** Missing CSP headers

**Recommendation:**
```python
response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline';"
)
```

---

#### Account Lockout
**Current:** Rate limiting per IP only

**Recommendation:**
- Add per-account failed attempt tracking
- Lock account after N failed attempts (e.g., 5)
- Require admin unlock or time-based unlock

---

#### Audit Logging
**Current:** Action logging but no persistence

**Recommendation:**
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource TEXT,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Track:
- Config changes
- Service control actions
- Device toggles
- Schedule modifications

---

## 5. Testing Recommendations

### 5.1 Unit Tests (Not Yet Implemented)

**Priority Test Coverage:**

```python
# tests/test_validators.py
def test_device_id_validation():
    # Valid device
    assert InputValidator.validate_device_id('LedProcessor')[0] == True

    # Invalid device
    assert InputValidator.validate_device_id('HackerDevice')[0] == False

    # SQL injection attempt
    assert InputValidator.validate_device_id("'; DROP TABLE users--")[0] == False

# tests/test_password_hashing.py
def test_bcrypt_hashing():
    password = "TestPassword123"
    hashed = User.hash_password(password)

    # Should start with bcrypt signature
    assert hashed.startswith('$2b$')

    # Should verify correctly
    assert User.verify_password(password, hashed) == True

    # Should reject wrong password
    assert User.verify_password("WrongPassword", hashed) == False
```

**Run tests:**
```bash
pytest tests/ -v --cov=app
```

---

## 6. Deployment Checklist

### Pre-Deployment

- [ ] Run password migration script
- [ ] Test login functionality with all users
- [ ] Verify database backup exists
- [ ] Review logs for errors
- [ ] Update `SECRET_KEY` in production environment
- [ ] Set `DEBUG=False` in production
- [ ] Configure HTTPS/TLS at reverse proxy level

### Post-Deployment

- [ ] Monitor login attempts for failures
- [ ] Check application logs for errors
- [ ] Verify all device control functions work
- [ ] Test service monitoring features
- [ ] Confirm schedule operations function correctly

### Security Verification

- [ ] Test invalid inputs are rejected
- [ ] Verify path traversal protection works
- [ ] Confirm rate limiting is active
- [ ] Check security headers are present
- [ ] Test session timeout behavior

---

## 7. File Changes Summary

### Modified Files

| File | Changes | Lines Changed |
|------|---------|---------------|
| [`app/__init__.py`](app/__init__.py) | Enhanced documentation, type hints | ~50 |
| [`app/models/__init__.py`](app/models/__init__.py) | Bcrypt implementation, verification logic | ~80 |
| [`app/controllers/revpi_controller.py`](app/controllers/revpi_controller.py) | Input validation integration | ~30 |
| [`app/services/revpi_service.py`](app/services/revpi_service.py) | Removed debug print | ~1 |
| [`app/services/systemd_service.py`](app/services/systemd_service.py) | Removed debug print | ~1 |
| [`requirements.txt`](requirements.txt) | Added bcrypt | ~1 |

### New Files

| File | Purpose | Lines |
|------|---------|-------|
| [`app/utils/__init__.py`](app/utils/__init__.py) | Utils package initialization | 5 |
| [`app/utils/validators.py`](app/utils/validators.py) | Input validation framework | ~350 |
| [`scripts/migrate_passwords.py`](scripts/migrate_passwords.py) | Password migration tool | ~200 |
| [`IMPROVEMENTS.md`](IMPROVEMENTS.md) | This document | ~600+ |

### Total Impact
- **~1,400 lines** of new/modified code
- **0 breaking changes** (backward compatible with migration)
- **3 new files** added
- **6 files** modified

---

## 8. Performance Considerations

### Bcrypt Performance

**Computational Cost:**
- Bcrypt is intentionally slower than SHA-256
- Typical hash time: ~100-300ms per password (vs <1ms for SHA-256)
- **Impact:** Login operations slightly slower but more secure

**Mitigation:**
- Bcrypt rounds set to 12 (balanced security vs performance)
- Only affects login/registration operations
- Session-based auth minimizes repeated hashing

**Benchmarks:**
```python
import bcrypt
import timeit

password = b"TestPassword123"

# SHA-256 time
sha_time = timeit.timeit(
    lambda: hashlib.sha256(password + b"salt").hexdigest(),
    number=1000
)
print(f"SHA-256: {sha_time/1000:.4f}ms per hash")  # ~0.01ms

# Bcrypt time
bcrypt_time = timeit.timeit(
    lambda: bcrypt.hashpw(password, bcrypt.gensalt(12)),
    number=10
)
print(f"Bcrypt:  {bcrypt_time/10:.4f}ms per hash")  # ~150ms
```

---

## 9. Rollback Procedure

If migration causes issues:

1. **Stop the application:**
   ```bash
   sudo systemctl stop jebi-web
   ```

2. **Restore database backup:**
   ```bash
   cp dev_users.db.backup_YYYYMMDD_HHMMSS dev_users.db
   ```

3. **Revert code changes:**
   ```bash
   git stash  # Or use git checkout to revert specific files
   ```

4. **Restart application:**
   ```bash
   sudo systemctl start jebi-web
   ```

5. **Verify functionality:**
   - Test login with old credentials
   - Check application logs

---

## 10. Future Enhancements

### Planned Improvements

1. **Role-Based Access Control (RBAC)**
   - Add user roles (admin, operator, viewer)
   - Permission-based endpoint access
   - Audit trail per role

2. **Multi-Factor Authentication (MFA)**
   - TOTP-based 2FA (Google Authenticator)
   - Backup codes
   - Remember device option

3. **API Key Authentication**
   - Support for programmatic access
   - Key rotation mechanism
   - Per-key rate limits

4. **Enhanced Monitoring**
   - Prometheus metrics export
   - Health check endpoints
   - Performance dashboards

5. **Database Migration to PostgreSQL**
   - Support multi-instance deployments
   - Better concurrency handling
   - Advanced features (JSON columns, full-text search)

---

## 11. Support & Contact

### Documentation

- Main README: [`README.md`](README.md)
- Configuration Guide: [`config.py`](config.py)
- API Documentation: Coming soon

### Issue Reporting

If you encounter issues with the improvements:

1. Check logs: `logs/jebi_web.log`
2. Verify configuration: `config.py`
3. Review migration output: Database backup files
4. Test with backup database if needed

### Questions?

Contact the development team or create an issue in the repository.

---

## 12. Changelog

### Version 2.0 (2025-10-22)

**Added:**
- ✅ Bcrypt password hashing implementation
- ✅ Comprehensive input validation framework
- ✅ Password migration script
- ✅ Enhanced documentation and type hints

**Fixed:**
- ✅ Removed debug print statements
- ✅ Improved password verification logic
- ✅ Enhanced security in User model

**Security:**
- ✅ **CRITICAL**: Replaced weak SHA-256 hashing with bcrypt
- ✅ **HIGH**: Input validation prevents injection attacks
- ✅ **MEDIUM**: Path traversal protection for file operations

**Documentation:**
- ✅ Added comprehensive IMPROVEMENTS.md
- ✅ Created migration guide
- ✅ Enhanced inline code documentation

---

## Appendix A: Security Best Practices Applied

### OWASP Top 10 (2021) Compliance

| Risk | Status | Implementation |
|------|--------|----------------|
| A01 - Broken Access Control | ✅ Partial | Session-based auth, login_required decorator |
| A02 - Cryptographic Failures | ✅ **Fixed** | **Bcrypt password hashing** |
| A03 - Injection | ✅ **Fixed** | **Parameterized queries + input validation** |
| A04 - Insecure Design | ✅ Good | Separation of concerns, service layer |
| A05 - Security Misconfiguration | ⚠️ Partial | Security headers present, CSP missing |
| A06 - Vulnerable Components | ✅ Good | Up-to-date dependencies |
| A07 - Auth Failures | ✅ Partial | Rate limiting, secure hashing |
| A08 - Software/Data Integrity | ✅ Good | Git version control |
| A09 - Logging Failures | ✅ Good | Comprehensive logging |
| A10 - SSRF | ✅ N/A | No external requests from user input |

---

## Appendix B: Validation Examples

### Device ID Validation

```python
from app.utils.validators import InputValidator

# Valid devices (from config_map_revpi)
valid_devices = [
    'RelayProcessor',
    'RelayScreen',
    'LedProcessor',
    'LedScreen',
    'RelayLight',
    'LedLight'
]

for device in valid_devices:
    is_valid, _ = InputValidator.validate_device_id(device)
    assert is_valid == True

# Invalid attempts
invalid_attempts = [
    'HackerDevice',
    'DROP TABLE users',
    '../../../etc/passwd',
    None,
    '',
    123  # Not a string
]

for attempt in invalid_attempts:
    is_valid, error = InputValidator.validate_device_id(attempt)
    assert is_valid == False
    assert error is not None  # Error message provided
```

### Service Name Validation

```python
# Allowed services
allowed = ['jebi-switchboard-guard.service', 'jebi-switchboard.service']

for service in allowed:
    is_valid, _ = InputValidator.validate_service_name(service)
    assert is_valid == True

# Blocked services
blocked = [
    'nginx.service',  # Not in whitelist
    'custom',  # Missing .service extension
    'hack; rm -rf /',  # Injection attempt
    '../systemd/system/malicious.service'  # Path traversal
]

for service in blocked:
    is_valid, error = InputValidator.validate_service_name(service)
    assert is_valid == False
```

---

**End of Document**

For questions or support, please contact the development team.
