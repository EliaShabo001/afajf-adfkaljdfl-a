# db.py file 
from supabase import create_client
import uuid

# Supabase credentials
SUPABASE_URL = 'https://onvhyjlazgptfxhdlmrj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9udmh5amxhemdwdGZ4aGRsbXJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0OTQ0NTIsImV4cCI6MjA2NzA3MDQ1Mn0.Jy59fTbV5weHj4ySc4kubl0WbdMhQc-HueMXNMxY6Is'

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_questions():
    response = supabase.table("questions").select("*").order("id").execute()
    return response.data

def save_question(question):
    supabase.table("questions").insert(question).execute()

def save_batch_link(batch_id, link_token, subject, number_of_questions, duration_minutes):
    from datetime import datetime, timedelta

    telegram_link = f"https://t.me/TestStudentCollegeBot?start=quiz_{link_token}"

    # Calculate expiry time (2 hours from now)
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=2)

    # Upsert batch metadata
    supabase.table("batches_metadata").upsert({
        "batch_id": batch_id,
        "subject": subject,
        "number_of_questions": number_of_questions,
        "duration_minutes": duration_minutes
    }).execute()

    # Upsert batch link info (use upsert to prevent duplicate key errors)
    supabase.table("batch_links").upsert({
        "batch_id": batch_id,
        "link_token": link_token,
        "telegram_link": telegram_link,
        "used": False,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat()
    }).execute()

def is_link_used(link_token):
    response = supabase.table("batch_links").select("used").eq("link_token", link_token).execute()
    if not response.data:
        return True
    return response.data[0]["used"]

def is_link_expired(link_token):
    """Check if a quiz link has expired (2 hours after creation)"""
    from datetime import datetime

    response = supabase.table("batch_links").select("expires_at, used").eq("link_token", link_token).execute()
    if not response.data:
        return True  # Link doesn't exist, consider it expired

    link_data = response.data[0]

    # If already used, it's effectively expired
    if link_data.get("used", False):
        return True

    # Check if expiry time has passed
    expires_at_str = link_data.get("expires_at")
    if not expires_at_str:
        return False  # No expiry set, assume not expired

    try:
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        now = datetime.now()

        # If current time is past expiry time, mark as expired
        if now > expires_at:
            # Auto-expire the link by marking it as used
            mark_link_expired(link_token)
            return True

        return False
    except Exception as e:
        print(f"Error checking expiry for token {link_token}: {e}")
        return False

def mark_link_expired(link_token):
    """Mark a link as expired by setting used=True"""
    try:
        # Mark batch_links as used (expired)
        supabase.table("batch_links").update({"used": True}).eq("link_token", link_token).execute()

        # Also mark all questions in the batch as used
        resp = supabase.table("batch_links").select("batch_id").eq("link_token", link_token).execute()
        if resp.data:
            batch_id = resp.data[0]["batch_id"]
            supabase.table("questions").update({"used": True}).eq("batch_id", batch_id).execute()
    except Exception as e:
        print(f"Error marking link as expired: {e}")

def mark_link_used(link_token):
    # Mark batch_links as used
    supabase.table("batch_links").update({"used": True}).eq("link_token", link_token).execute()
    
    # Also mark all questions in the batch as used
    resp = supabase.table("batch_links").select("batch_id").eq("link_token", link_token).execute()
    if resp.data:
        batch_id = resp.data[0]["batch_id"]
        supabase.table("questions").update({"used": True}).eq("batch_id", batch_id).execute()

def load_questions_by_batch(link_token):
    response = supabase.table("batch_links").select("batch_id").eq("link_token", link_token).execute()
    if not response.data:
        return None
    batch_id = response.data[0]["batch_id"]
    response = supabase.table("questions").select("*").eq("batch_id", batch_id).execute()
    if not response.data:
        return None
    return response.data

def get_telegram_link(link_token):
    response = supabase.table("batch_links").select("telegram_link").eq("link_token", link_token).execute()
    if not response.data:
        return None
    return response.data[0]["telegram_link"]

def get_batch_metadata(link_token):
    """Get batch metadata including duration for a specific link token"""
    # First get batch_id from link_token
    response = supabase.table("batch_links").select("batch_id").eq("link_token", link_token).execute()
    if not response.data:
        return None

    batch_id = response.data[0]["batch_id"]

    # Get metadata for this batch
    meta_resp = supabase.table("batches_metadata").select("*").eq("batch_id", batch_id).execute()
    if not meta_resp.data:
        return None

    return meta_resp.data[0]

def get_all_subjects():
    """Get all unique subject names from existing batches"""
    meta_resp = supabase.table("batches_metadata").select("subject").execute()
    if not meta_resp.data:
        return []

    subjects = list(set([batch["subject"] for batch in meta_resp.data if batch.get("subject")]))
    return sorted(subjects)

def get_questions_by_subject(subject):
    """Get all questions for a specific subject"""
    response = supabase.table("questions").select("*").eq("subject", subject).order("id").execute()
    return response.data

def update_question(question_id, updated_data):
    """Update a specific question"""
    response = supabase.table("questions").update(updated_data).eq("id", question_id).execute()
    return response.data

def get_question_by_id(question_id):
    """Get a specific question by ID"""
    response = supabase.table("questions").select("*").eq("id", question_id).execute()
    if response.data:
        return response.data[0]
    return None

def get_actual_question_count_by_batch(batch_id):
    """Get the actual current count of questions for a batch"""
    response = supabase.table("questions").select("id").eq("batch_id", batch_id).execute()
    return len(response.data) if response.data else 0

def update_batch_metadata_question_count(batch_id):
    """Update the question count in batches_metadata to match actual questions"""
    actual_count = get_actual_question_count_by_batch(batch_id)
    supabase.table("batches_metadata").update({
        "number_of_questions": actual_count
    }).eq("batch_id", batch_id).execute()
    return actual_count

def get_all_batches():
    from datetime import datetime

    meta_resp = supabase.table("batches_metadata").select("*").execute()
    if not meta_resp.data:
        return []

    metadata = meta_resp.data
    links_resp = supabase.table("batch_links").select("*").execute()
    if not links_resp.data:
        return []

    links = links_resp.data
    links_map = {l["batch_id"]: l for l in links}

    batches = []
    for batch in metadata:
        batch_id = batch["batch_id"]
        link_info = links_map.get(batch_id, {})

        # Check if link is expired
        is_expired = False
        expires_at_str = link_info.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                now = datetime.now()
                is_expired = now > expires_at
            except:
                is_expired = False

        batches.append({
            "batch_id": batch_id,
            "subject": batch.get("subject", ""),
            "question_count": batch.get("number_of_questions", 0),
            "time": batch.get("duration_minutes", 15),
            "telegram_link": link_info.get("telegram_link", ""),
            "used": link_info.get("used", False),
            "expired": is_expired,
            "created_at": link_info.get("created_at", ""),
            "expires_at": link_info.get("expires_at", "")
        })
    return batches

def reactivate_batch_link(batch_id):
    """Reactivate a batch link by setting used=False and extending expiry time"""
    from datetime import datetime, timedelta

    try:
        # Calculate new expiry time (2 hours from now)
        new_expires_at = datetime.now() + timedelta(hours=2)

        # Reactivate batch link with new expiry time
        supabase.table("batch_links").update({
            "used": False,
            "expires_at": new_expires_at.isoformat()
        }).eq("batch_id", batch_id).execute()

        # Reactivate all questions in the batch
        supabase.table("questions").update({"used": False}).eq("batch_id", batch_id).execute()

        return True
    except Exception as e:
        print(f"Error reactivating batch {batch_id}: {e}")
        return False

def get_batch_info_by_id(batch_id):
    """Get detailed batch information including metadata and link info"""
    # Get metadata
    meta_resp = supabase.table("batches_metadata").select("*").eq("batch_id", batch_id).execute()
    if not meta_resp.data:
        return None

    metadata = meta_resp.data[0]

    # Get link info
    link_resp = supabase.table("batch_links").select("*").eq("batch_id", batch_id).execute()
    if not link_resp.data:
        return None

    link_info = link_resp.data[0]

    return {
        "batch_id": batch_id,
        "subject": metadata.get("subject", ""),
        "question_count": metadata.get("number_of_questions", 0),
        "duration_minutes": metadata.get("duration_minutes", 15),
        "telegram_link": link_info.get("telegram_link", ""),
        "link_token": link_info.get("link_token", ""),
        "used": link_info.get("used", False)
    }
