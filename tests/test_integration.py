"""
Integration tests for WhatsApp KYC System

Tests the full pipeline components work together.
Run with: pytest tests/test_integration.py -v -s
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base, Employee, KYCSubmission, Document


class TestDatabaseIntegration:
    """Integration tests for database operations"""

    @pytest.fixture(scope="function")
    def real_db(self):
        """Create real test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        yield SessionLocal()
        Base.metadata.drop_all(engine)

    def test_employee_creation_and_retrieval(self, real_db):
        """Test creating and retrieving employee"""
        employee = Employee(
            id="emp-001",
            phone_number="+919876543210"
        )
        real_db.add(employee)
        real_db.commit()

        retrieved = real_db.query(Employee).filter_by(phone_number="+919876543210").first()
        assert retrieved is not None
        assert retrieved.id == "emp-001"
        assert retrieved.phone_number == "+919876543210"

    def test_kyc_submission_with_relationships(self, real_db):
        """Test creating KYC submission with documents"""
        # Create employee
        employee = Employee(id="emp-002", phone_number="+919876543211")
        real_db.add(employee)
        real_db.commit()

        # Create submission
        submission = KYCSubmission(
            id="sub-001",
            employee_id="emp-002",
            status="PENDING",
            pan_name="TEST USER"
        )
        real_db.add(submission)
        real_db.commit()

        # Create document
        document = Document(
            id="doc-001",
            kyc_submission_id="sub-001",
            document_type="PAN_CARD",
            file_path="test.jpg"
        )
        real_db.add(document)
        real_db.commit()

        # Retrieve with relationships
        retrieved_submission = real_db.query(KYCSubmission).filter_by(id="sub-001").first()
        assert retrieved_submission is not None
        assert retrieved_submission.employee.phone_number == "+919876543211"
        assert len(retrieved_submission.documents) == 1
        assert retrieved_submission.documents[0].document_type == "PAN_CARD"

    def test_multiple_submissions_per_employee(self, real_db):
        """Test employee can have multiple KYC submissions"""
        # Create employee
        employee = Employee(id="emp-003", phone_number="+919876543212")
        real_db.add(employee)
        real_db.commit()

        # Create first submission
        submission1 = KYCSubmission(
            id="sub-002",
            employee_id="emp-003",
            status="PENDING"
        )
        real_db.add(submission1)

        # Create second submission
        submission2 = KYCSubmission(
            id="sub-003",
            employee_id="emp-003",
            status="APPROVED"
        )
        real_db.add(submission2)
        real_db.commit()

        # Verify employee has 2 submissions
        retrieved_employee = real_db.query(Employee).filter_by(id="emp-003").first()
        assert len(retrieved_employee.kyc_submissions) == 2
        statuses = [s.status for s in retrieved_employee.kyc_submissions]
        assert "PENDING" in statuses
        assert "APPROVED" in statuses

    def test_document_types(self, real_db):
        """Test all three document types can be stored"""
        # Create employee and submission
        employee = Employee(id="emp-004", phone_number="+919876543213")
        real_db.add(employee)
        real_db.commit()

        submission = KYCSubmission(
            id="sub-004",
            employee_id="emp-004",
            status="PENDING"
        )
        real_db.add(submission)
        real_db.commit()

        # Create all document types
        doc_types = ["PAN_CARD", "AADHAAR_CARD", "BANK_DOCUMENT"]
        for idx, doc_type in enumerate(doc_types):
            document = Document(
                id=f"doc-{idx+2}",
                kyc_submission_id="sub-004",
                document_type=doc_type,
                file_path=f"test_{doc_type.lower()}.jpg"
            )
            real_db.add(document)

        real_db.commit()

        # Verify all documents created
        retrieved_submission = real_db.query(KYCSubmission).filter_by(id="sub-004").first()
        assert len(retrieved_submission.documents) == 3

        retrieved_types = [d.document_type for d in retrieved_submission.documents]
        assert "PAN_CARD" in retrieved_types
        assert "AADHAAR_CARD" in retrieved_types
        assert "BANK_DOCUMENT" in retrieved_types

    def test_submission_status_updates(self, real_db):
        """Test updating submission status"""
        # Create employee and submission
        employee = Employee(id="emp-005", phone_number="+919876543214")
        real_db.add(employee)
        real_db.commit()

        submission = KYCSubmission(
            id="sub-005",
            employee_id="emp-005",
            status="PENDING"
        )
        real_db.add(submission)
        real_db.commit()

        # Update status
        submission.status = "APPROVED"
        submission.review_notes = "All documents verified"
        real_db.commit()

        # Verify update
        retrieved = real_db.query(KYCSubmission).filter_by(id="sub-005").first()
        assert retrieved.status == "APPROVED"
        assert retrieved.review_notes == "All documents verified"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
