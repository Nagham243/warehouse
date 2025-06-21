from django import forms
from club_dashboard.models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i}⭐") for i in range(1, 6)],
        label="التقييم",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    comment = forms.CharField(
        label="التعليق",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']




from django import forms
from club_dashboard.models import RefundDispute, RefundDisputeAttachment
from .widgets import MultipleFileInput
from django.core.files.uploadedfile import UploadedFile


class RefundDisputeForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=MultipleFileInput(attrs={'accept': 'image/*, .pdf, .doc, .docx, .txt, video/*'}),
        required=False,
        label="Attachments"
    )
    attachment_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Attachment Description"
    )

    class Meta:
        model = RefundDispute
        fields = ['title', 'deal', 'description', 'dispute_type',
                  'priority', 'refund_type', 'requested_refund_amount']
        # Removed 'attachments' and 'attachment_description' from fields as they're not model fields

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter deals to only show user's orders
        if self.user:
            # Assuming you have access to the Order model through students app
            from students.models import Order
            self.fields['deal'].queryset = Order.objects.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()

        # Validate that requested refund amount doesn't exceed deal amount
        deal = cleaned_data.get('deal')
        requested_amount = cleaned_data.get('requested_refund_amount')

        if deal and requested_amount:
            if requested_amount > deal.total_price:
                raise forms.ValidationError({
                    'requested_refund_amount': 'Requested refund cannot exceed the original deal amount.'
                })

        # Validate that the deal belongs to the current user
        if deal and self.user and deal.user != self.user:
            raise forms.ValidationError({
                'deal': 'You can only create disputes for your own orders.'
            })

        return cleaned_data

    def save(self, commit=True):
        dispute = super().save(commit=False)

        # Set the client to the current user
        if self.user:
            dispute.client = self.user

        # Auto-populate vendor and original_amount from deal
        if dispute.deal:
            # Set original amount from deal
            dispute.original_amount = dispute.deal.total_price

            # Set vendor from first item in the deal
            first_item = dispute.deal.items.first()
            if first_item:
                if hasattr(first_item, 'product') and first_item.product:
                    dispute.vendor = first_item.product.creator
                elif hasattr(first_item, 'service') and first_item.service:
                    dispute.vendor = first_item.service.creator

        if commit:
            dispute.save()
            # Save attachments after the dispute is saved
            self.save_attachments(dispute)

        return dispute

    def save_attachments(self, dispute):
        """Save uploaded attachments"""
        if 'attachments' in self.files:
            files = self.files.getlist('attachments')
            description = self.cleaned_data.get('attachment_description', '')

            for file in files:
                file_type = self.determine_file_type(file)
                RefundDisputeAttachment.objects.create(
                    refund_dispute=dispute,
                    file=file,
                    description=description,
                    uploaded_by=self.user,
                    file_type=file_type
                )

    def determine_file_type(self, file: UploadedFile) -> str:
        """Determine file type based on content type and extension"""
        if not isinstance(file, UploadedFile):
            return 'other'

        # Check content type first
        if hasattr(file, 'content_type') and file.content_type:
            content_type = file.content_type.split('/')[0]
            if content_type == 'image':
                return 'image'
            elif content_type == 'video':
                return 'video'

        # Check file extension
        if hasattr(file, 'name') and file.name:
            if file.name.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                return 'document'
            elif file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                return 'image'
            elif file.name.lower().endswith(('.mp4', '.avi', '.mov', '.wmv')):
                return 'video'

        return 'other'
