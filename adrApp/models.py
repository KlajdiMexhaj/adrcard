from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import time
import random
import uuid
from django.db.models.signals import pre_save

class Anetaret(models.Model):
    GJINIA_CHOICES = [
        ('Mashkull', 'Mashkull'),
        ('Femër', 'Femër'),
    ]
    STATUSI_CHOICES = [
        ('Martuar', 'Martuar'),
        ('Beqar', 'Beqar'),
    ]
    STATUS_CHOICES = [
        ('Aktiv', 'Aktiv'),
        ('I heshtur', 'I heshtur'),
    ]
    ARSIMI_CHOISE =[
        ('I ulët','I ulët'),
        ('I mesëm', 'I mesëm'),
        ('I lartë','I lartë'),
    ]
    id = models.AutoField(primary_key=True)
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    emer = models.CharField(max_length=100)
    mbiemer = models.CharField(max_length=100)
    karta_identitetit= models.CharField(max_length=20, unique=True,null=True,blank=True)
    nr_tel = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    gjinia = models.CharField(max_length=10, choices=GJINIA_CHOICES)
    mosha = models.IntegerField()
    datelindja = models.DateField()
    vendlindja = models.CharField(max_length=100)
    vendbanimi = models.CharField(max_length=100)
    adresa = models.CharField(max_length=100)
    profesioni = models.CharField(max_length=100)
    arsimi = models.CharField(max_length=10,choices=ARSIMI_CHOISE)
    shkolla = models.CharField(max_length=100,blank=True,null=True)
    gjuhet_e_foluar = models.CharField(max_length=100)
    statusi = models.CharField(max_length=10, choices=STATUSI_CHOICES)
    sa_femijë_ka = models.IntegerField()
    foto = models.ImageField(upload_to='anetaret_foto/')
    created_at = models.DateTimeField(auto_now_add=True)
    status_i_kartës = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Aktiv')

    otp_code = models.IntegerField(null=True, blank=True)  
    def __str__(self):
        return self.emer
    

# Function to generate a 6-digit OTP
def generate_otp_code():
    return random.randint(100000, 999999)

# Signal to automatically generate the OTP before saving the instance
@receiver(pre_save, sender=Anetaret)
def generate_otp(sender, instance, **kwargs):
    if not instance.otp_code:  # Only generate if no OTP exists
        instance.otp_code = generate_otp_code()

def update_status_to_iheshtur(instance):
    random_time_in_seconds = random.randint(60, 365 * 24 * 3600)
    
    # Sleep for the random time
    time.sleep(random_time_in_seconds)
    
    # Update the status after the time period
    instance.status_i_kartës = 'I heshtur'
    instance.save()

@receiver(post_save, sender=Anetaret)
def check_and_update_status(sender, instance, created, **kwargs):
    if instance.status_i_kartës == 'Aktiv':
        # Run the background task in a separate thread
        threading.Thread(target=update_status_to_iheshtur, args=(instance,)).start()



class Propozimet(models.Model):
    CATEGORY_CHOICES = [
        ('option1', 'Propozim për kandidat për deputet'),
        ('option2', 'Propozim për programin'),
        ('option3', 'Propozim për evente'),
        ('option4', 'Propozim për kandidatët e organigramës'),
    ]

    user = models.ForeignKey('Anetaret', on_delete=models.CASCADE)
    text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    cv = models.FileField(upload_to='cv_uploads/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user.id} - {self.get_category_display()}"
    

class Propozimet_per_Aprovim(models.Model):
    propozim = models.ForeignKey(Propozimet, on_delete=models.CASCADE)
    user = models.ForeignKey('Anetaret', on_delete=models.CASCADE)
    choice = models.CharField(max_length=2, choices=[('Po', 'Po'), ('Jo', 'Jo')])
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)  # You add a field to store the text
    cv = models.FileField(upload_to='cv_uploads/', blank=True, null=True)

    class Meta:
        unique_together = ('propozim', 'user')  # Ensure one response per user per proposal

    def save(self, *args, **kwargs):
        if not self.text:  # Check if the text field is empty
            self.text = self.propozim.text  # Set the text field from related Propozimet model
        if not self.cv:
            self.cv = self.propozim.cv
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.id} - {self.user.emer} {self.user.mbiemer} - {self.propozim.id}  - {self.choice}"

class Propozimet_per_Votim(models.Model):
    propozim = models.ForeignKey(Propozimet, on_delete=models.CASCADE)
    user = models.ForeignKey('Anetaret', on_delete=models.CASCADE)
    choice = models.CharField(max_length=10, choices=[('Po', 'Po'), ('Jo', 'Jo'), ('Abstenim', 'Abstenim')])
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    cv = models.FileField(upload_to='cv_uploads/', blank=True, null=True)

    class Meta:
        unique_together = ('propozim', 'user')  # Ensure one response per user per proposal

    def save(self, *args, **kwargs):
        if not self.text:  
            self.text = self.propozim.text  
        if not self.cv:
            self.cv = self.propozim.cv
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.id} - {self.user.emer} {self.user.mbiemer} - {self.propozim.id} - {self.choice}"



class Event(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    event_date = models.DateField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date_created']
    def __str__(self):
        return self.title
    

class KandidatPerDeputet(models.Model):
    emer = models.CharField(max_length=50)
    mbiemer = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.emer
    


class Komunikime_Zyrtare(models.Model):
    titull = models.CharField(max_length=200,null=True,blank=True)
    text = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.titull if self.titull else "No Title"
