from django.contrib import admin
from .models import *
from django.shortcuts import render
from django.http import FileResponse,HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from .views import generate_user_pdf 
from django.utils.html import format_html
from django.urls import path
from reportlab.lib.pagesizes import  landscape,letter
# Register your models here.
from PIL import Image
def generate_access_card_pdf(modeladmin, request, queryset):
    for user in queryset:
        # Define paths
        qr_code_path = os.path.join(settings.MEDIA_ROOT, f'qr_code/{user.guid}.jpg')
        static_image_path = os.path.join(settings.BASE_DIR, 'adrApp', 'static', 'img', 'KARTA-ADR_page-0001.jpg')

        if not os.path.exists(static_image_path):
            raise FileNotFoundError(f"Static image not found: {static_image_path}")
        if not os.path.exists(qr_code_path):
            raise FileNotFoundError(f"QR code image not found: {qr_code_path}")

        # Define output PDF path in Downloads
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", f"{user.guid}_access_card.pdf")

        # Set PDF dimensions (320x210 px)
        page_width, page_height = 320, 210

        # Resize images **before** adding to PDF to avoid white borders
        def resize_image(image_path, output_size):
            img = Image.open(image_path)
            img = img.resize(output_size, Image.LANCZOS)  # High-quality resizing
            temp_path = image_path.replace(".jpg", "_resized.jpg")  # Temporary resized image
            img.save(temp_path, quality=100)  # Save with max quality
            return temp_path

        static_resized = resize_image(static_image_path, (page_width, page_height))
        qr_resized = resize_image(qr_code_path, (page_width, page_height))

        # Create PDF
        c = canvas.Canvas(downloads_path, pagesize=(page_width, page_height))

        # Add images **full size**, no white borders
        c.drawImage(static_resized, 0, 0, width=page_width, height=page_height, mask=None)
        c.showPage()
        c.drawImage(qr_resized, 0, 0, width=page_width, height=page_height, mask=None)
        c.showPage()

        c.save()

        # Open the PDF automatically
        os.startfile(downloads_path)

        # Remove temp images after saving
        os.remove(static_resized)
        os.remove(qr_resized)

    return None

# Register in Django Admin
class AnetaretAdmin(admin.ModelAdmin):
    list_display = ('id', 'emer', 'mbiemer', 'status_i_kartës', 'guid')
    list_display_links = ('id', 'emer', 'mbiemer', 'status_i_kartës')
    search_fields = ('emer', 'mbiemer')
    actions = [generate_access_card_pdf]

admin.site.register(Anetaret, AnetaretAdmin)

class PropozimetAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'category', 'created_at', 'cv')  # Add 'cv' to the list_display
    list_filter = ('category', 'created_at')  # Optionally add filters
    search_fields = ('user__emer', 'category')  # Optionally add search functionality for user or category

admin.site.register(Propozimet, PropozimetAdmin)
class PropozimetStatusAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view of the admin
    list_display = ('user', 'propozim', 'text', 'cv', 'choice', 'created_at')  # Add or modify fields as per your requirements
    # Optionally, you can also add ordering in the admin interface
    ordering = ['-created_at']  # Orders by creation date in descending order

    # Add search functionality
    search_fields = ['user__emer', 'user__mbiemer', 'propozim__text']  # Allow searching by user name or proposal text

    # Add filter options
    list_filter = ['choice', 'created_at']  # Filter by choice and creation date

    # Exclude `created_at` from the form in the admin panel since it's not editable
    exclude = ('created_at',)

    # Optionally, if you want to edit these fields inline
    fieldsets = (
        (None, {
            'fields': ('user', 'propozim', 'text', 'cv', 'choice')
        }),
    )

# Register the model with the custom admin interface
admin.site.register(Propozimet_per_Aprovim, PropozimetStatusAdmin)

admin.site.register(Propozimet_per_Votim)

admin.site.register(Event)
admin.site.register(KandidatPerDeputet)
admin.site.register(Komunikime_Zyrtare)