# tests/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.database import Base, Employee, KYCSubmission, Document, AuditLog

def test_employee_model_creation():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    employee = Employee(
        id='test-id',
        phone_number='+919876543210'
    )
    session.add(employee)
    session.commit()

    assert employee.phone_number == '+919876543210'
    session.close()


def test_all_models_and_relationships():
    """Test all models and their relationships"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create employee
    employee = Employee(
        id='emp-001',
        phone_number='+919876543210'
    )
    session.add(employee)
    session.commit()

    # Create KYC submission
    kyc_submission = KYCSubmission(
        id='kyc-001',
        employee_id='emp-001',
        status='pending',
        pan_number_encrypted='encrypted_pan',
        pan_name='Test User',
        pan_confidence=0.95,
        aadhaar_last4='1234',
        aadhaar_name='Test User',
        aadhaar_confidence=0.98,
        bank_account_encrypted='encrypted_account',
        bank_holder_name='Test User',
        bank_ifsc='SBIN0001234',
        bank_confidence=0.92,
        name_match_score=0.96,
        overall_confidence=0.95
    )
    session.add(kyc_submission)
    session.commit()

    # Create document
    document = Document(
        id='doc-001',
        kyc_submission_id='kyc-001',
        document_type='pan',
        file_path='/uploads/pan.pdf',
        file_size=1024,
        extraction_method='claude'
    )
    session.add(document)
    session.commit()

    # Create audit log
    audit_log = AuditLog(
        event_type='kyc_submitted',
        employee_id='emp-001',
        kyc_submission_id='kyc-001',
        performed_by='system',
        details='KYC submission created',
        ip_address='127.0.0.1'
    )
    session.add(audit_log)
    session.commit()

    # Test relationships
    retrieved_employee = session.query(Employee).filter_by(id='emp-001').first()
    assert len(retrieved_employee.kyc_submissions) == 1
    assert retrieved_employee.kyc_submissions[0].status == 'pending'

    retrieved_kyc = session.query(KYCSubmission).filter_by(id='kyc-001').first()
    assert retrieved_kyc.employee.phone_number == '+919876543210'
    assert len(retrieved_kyc.documents) == 1
    assert retrieved_kyc.documents[0].document_type == 'pan'

    # Test cascade delete
    session.delete(employee)
    session.commit()

    # Verify cascade delete worked
    assert session.query(KYCSubmission).filter_by(id='kyc-001').first() is None
    assert session.query(Document).filter_by(id='doc-001').first() is None

    session.close()


def test_init_database_function():
    """Test the init_database function"""
    import os
    import tempfile
    from src.models.database import init_database
    from sqlalchemy import create_engine

    # Create a temporary database file
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, 'test.db')

        # Set environment variable for test
        os.environ['DATABASE_PATH'] = db_path

        # Initialize database
        init_database()

        # Verify database file was created
        assert os.path.exists(db_path)

        # Verify tables exist by connecting
        engine = create_engine(f'sqlite:///{db_path}')
        from src.models.database import Base
        assert 'employees' in Base.metadata.tables
        assert 'kyc_submissions' in Base.metadata.tables
        assert 'documents' in Base.metadata.tables
        assert 'audit_logs' in Base.metadata.tables
        engine.dispose()

    finally:
        # Clean up on Windows
        import shutil
        try:
            shutil.rmtree(tmpdir)
        except PermissionError:
            pass  # Ignore cleanup errors on Windows


def test_get_session_function():
    """Test the get_session function"""
    import os
    import tempfile
    from src.models.database import init_database, get_session

    # Create a temporary database file
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, 'test.db')

        # Set environment variable for test
        os.environ['DATABASE_PATH'] = db_path

        # Initialize database
        init_database()

        # Get session
        session = get_session()
        assert session is not None

        # Test session works
        employee = Employee(
            id='test-emp',
            phone_number='+919999999999'
        )
        session.add(employee)
        session.commit()

        retrieved = session.query(Employee).filter_by(id='test-emp').first()
        assert retrieved is not None
        assert retrieved.phone_number == '+919999999999'

        session.close()

        # Properly dispose engine
        session.get_bind().dispose()

    finally:
        # Clean up on Windows
        import shutil
        try:
            shutil.rmtree(tmpdir)
        except PermissionError:
            pass  # Ignore cleanup errors on Windows
