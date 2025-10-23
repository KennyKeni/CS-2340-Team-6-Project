"""
Shared messaging utilities for handling conversations between users.
"""
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from recruiter.models import Message

User = get_user_model()


def get_messages_context(request):
    """
    Get context data for messages list view.

    This function handles the common logic for displaying conversations
    that is shared between recruiter and applicant message views.

    Args:
        request: The HTTP request object

    Returns:
        dict: Context dictionary containing:
            - conversations: List of conversation data
            - selected_conversation: Selected conversation details (if any)
    """
    # Get all unique conversations (people the user has messaged or been messaged by)
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True).distinct()
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True).distinct()

    # Get all conversation partners
    all_conversation_partners = set(sent_to) | set(received_from)

    # Create conversation data with latest message and unread count
    conversations = []
    for partner_id in all_conversation_partners:
        partner = User.objects.get(id=partner_id)

        # Get latest message in this conversation
        latest_message = Message.objects.filter(
            Q(sender=request.user, recipient=partner) |
            Q(sender=partner, recipient=request.user)
        ).order_by('-created_at').first()

        # Count unread messages from this partner
        unread_count = Message.objects.filter(
            sender=partner,
            recipient=request.user,
            is_read=False
        ).count()

        # Mark messages as read when viewing conversation
        if request.GET.get('partner_id') == str(partner_id):
            Message.objects.filter(
                sender=partner,
                recipient=request.user,
                is_read=False
            ).update(is_read=True)

        conversations.append({
            'partner': partner,
            'latest_message': latest_message,
            'unread_count': unread_count,
            'is_active': request.GET.get('partner_id') == str(partner_id)
        })

    # Sort conversations by latest message date
    conversations.sort(key=lambda x: x['latest_message'].created_at if x['latest_message'] else timezone.now() - timezone.timedelta(days=365), reverse=True)

    # Get messages for selected conversation
    selected_conversation = None
    if request.GET.get('partner_id'):
        try:
            partner = User.objects.get(id=request.GET.get('partner_id'))
            conversation_messages = Message.objects.filter(
                Q(sender=request.user, recipient=partner) |
                Q(sender=partner, recipient=request.user)
            ).select_related('sender', 'recipient', 'related_job').order_by('created_at')

            selected_conversation = {
                'partner': partner,
                'messages': conversation_messages
            }
        except User.DoesNotExist:
            pass

    return {
        'conversations': conversations,
        'selected_conversation': selected_conversation,
    }
