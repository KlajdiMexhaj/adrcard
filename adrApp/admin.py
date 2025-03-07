from django.contrib import admin
from .models import *
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
# Register your models here.
class AnetaretAdmin(admin.ModelAdmin):
    list_display = ('id','emer','mbiemer','status_i_kartës','guid')
    list_display_links = ('id','emer','mbiemer','status_i_kartës')
    search_fields = ('emer','mbiemer')
    
    # Add a custom action for printing the card
    actions = ['print_card']

    def print_card(self, request, queryset):
        # Generate the print card for each selected user
        for anetaret in queryset:
            # Create a context with the unique QR code and other data for the card
            context = {
                'anetaret': anetaret,
                'qr_code_url': anetaret.qr_code_path.url,  # Assuming this field stores the file path of the QR code
            }

            # Render the print card template (this will generate the HTML for the card)
            html_content = render_to_string('printcard.html', context)

            # Create the response as a PDF or HTML file (you can use a library like WeasyPrint to generate PDFs if needed)
            response = HttpResponse(html_content, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=printcard.pdf'

            return response

        # If nothing is selected, show a message
        self.message_user(request, "No user selected to print.")
    print_card.short_description = "Print Selected Cards"
    
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