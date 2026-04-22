#!/usr/bin/env python3
"""
Real-time KYC Submission Watcher

This script polls the API every 2 seconds and displays new submissions.
Perfect for testing - run this while someone submits documents via WhatsApp.

Usage:
    python watch_submissions.py

Requirements:
    pip install requests
"""

import requests
import time
import json
from datetime import datetime
from typing import Set

# Configuration
API_URL = "http://192.168.1.49:8000"
API_KEY = "metro-kyc-secure-key-2026"
POLL_INTERVAL = 2  # seconds


def get_submissions():
    """Fetch all submissions from API."""
    try:
        response = requests.get(
            f"{API_URL}/api/submissions",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return None


def display_submission(sub):
    """Pretty print a submission."""
    print("\n" + "="*70)
    print(f"📋 Submission ID: {sub['id'][:8]}...")
    print(f"📱 Phone: {sub['phone_number']}")
    print(f"⏰ Submitted: {sub['submitted_at']}")
    print(f"📊 Status: {sub['status']}")
    print(f"🎯 Confidence: {sub['overall_confidence']}")
    print("="*70)


def get_submission_details(submission_id):
    """Fetch detailed submission data."""
    try:
        response = requests.get(
            f"{API_URL}/api/submissions/{submission_id}",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching details: {e}")
        return None


def display_details(data):
    """Display extracted document data."""
    print("\n📄 Extracted Data:")

    # Aadhaar
    if data.get('aadhaar_name'):
        print(f"\n  🆔 AADHAAR CARD:")
        print(f"     Name: {data['aadhaar_name']}")
        print(f"     Last 4: {data['aadhaar_last4']}")
        print(f"     DOB: {data['aadhaar_dob']}")
        print(f"     Gender: {data['aadhaar_gender']}")
        print(f"     Confidence: {data['aadhaar_confidence']}")

    # PAN
    if data.get('pan_name'):
        print(f"\n  💳 PAN CARD:")
        print(f"     Name: {data['pan_name']}")
        print(f"     Father: {data['pan_father_name']}")
        print(f"     DOB: {data['pan_dob']}")
        print(f"     Confidence: {data['pan_confidence']}")

    # Bank
    if data.get('bank_holder_name'):
        print(f"\n  🏦 BANK DOCUMENT:")
        print(f"     Name: {data['bank_holder_name']}")
        print(f"     Bank: {data['bank_name']}")
        print(f"     IFSC: {data['bank_ifsc']}")
        print(f"     Branch: {data['bank_branch']}")
        print(f"     Confidence: {data['bank_confidence']}")

    # Name matching
    if data.get('name_match_score'):
        print(f"\n  ✅ Name Match Score: {data['name_match_score']:.2f}")


def watch():
    """Main watch loop."""
    seen_ids: Set[str] = set()

    print("🔍 KYC Submission Watcher")
    print(f"📡 Connected to: {API_URL}")
    print(f"⏱️  Polling every {POLL_INTERVAL} seconds")
    print("🛑 Press Ctrl+C to stop\n")

    try:
        while True:
            result = get_submissions()

            if result is None:
                print("⚠️  Retrying in 5 seconds...")
                time.sleep(5)
                continue

            submissions = result.get('submissions', [])

            # Check for new submissions
            for sub in submissions:
                sub_id = sub['id']
                if sub_id not in seen_ids:
                    seen_ids.add(sub_id)
                    print(f"\n🆕 NEW SUBMISSION DETECTED!")
                    display_submission(sub)

                    # Fetch and display details
                    details = get_submission_details(sub_id)
                    if details:
                        display_details(details)

            # Show current count
            print(f"\r👁️  Watching... ({len(submissions)} total submissions)", end='', flush=True)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n✋ Stopped watching")


if __name__ == "__main__":
    watch()
