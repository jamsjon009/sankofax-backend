from PIL import Image as PILImage
import io
from django.core.files.uploadedfile import InMemoryUploadedFile


def optimize_image(image_field, max_size=(1200, 1200), quality=85):
    """Resize and compress an image file. Returns optimized InMemoryUploadedFile."""
    try:
        img = PILImage.open(image_field)
        img = img.convert('RGB')
        img.thumbnail(max_size, PILImage.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)

        name_parts = image_field.name.rsplit('.', 1)
        new_name = f"{name_parts[0]}.jpg"

        return InMemoryUploadedFile(
            output, 'ImageField', new_name,
            'image/jpeg', output.getbuffer().nbytes, None
        )
    except Exception:
        return image_field  # fallback: return original if Pillow fails