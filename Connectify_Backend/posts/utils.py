import os
import cloudinary
import cloudinary.uploader
from django.conf import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_to_cloudinary(file, folder='posts'):
    """Upload media file to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto",
            quality="auto",
            fetch_format="auto",
        )
        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type']
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_from_cloudinary(public_id):
    """Delete media file from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}
