from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'get_full_name', 'status', 'compliance_status', 'date_joined')
    list_filter = ('status', 'compliance_status', 'date_joined')
    search_fields = ('member_id', 'user__username', 'user__first_name', 'user__last_name', 'user__phone')
    raw_id_fields = ('user',)
    readonly_fields = ('member_id', 'date_joined')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
