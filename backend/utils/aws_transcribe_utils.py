#backend/utils/aws_transcribe_utils.py
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from backend.utils.performance_utils import timeit

@timeit
def upload_audio_to_s3(local_audio_path, s3_bucket, s3_key):
    """
    Uploads a local audio file to an S3 bucket.
    Returns (success: bool, message_or_url: str).
    """
    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(str(local_audio_path), s3_bucket, s3_key)
        http_url = f"https://{s3_bucket}.s3.{s3_client.meta.region_name}.amazonaws.com/{s3_key}"
        return True, http_url
    except (BotoCoreError, ClientError) as e:
        return False, f"S3 Upload failed: {e}"

def start_transcription_job(job_name, media_uri, language_code="en-IN"):
    """
    Starts an AWS Transcribe job and returns (job_name, error).
    """
    transcribe = boto3.client("transcribe")
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat="wav",
            LanguageCode=language_code,
        )
        return response["TranscriptionJob"]["TranscriptionJobName"], None
    except Exception as e:
        return None, f"Failed to start transcription job: {e}"

def get_transcription_status(job_name):
    """
    Checks the status of a transcription job.
    Returns (status, transcript_uri, error) where status can be 'IN_PROGRESS', 'COMPLETED', or 'FAILED'.
    transcript_uri will contain the URL to the transcript file if completed.
    """
    transcribe = boto3.client("transcribe")
    try:
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        transcript_uri = None
        if status == 'COMPLETED':
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        return status, transcript_uri, None
    except Exception as e:
        return None, None, f"Failed to get transcription status: {e}"
