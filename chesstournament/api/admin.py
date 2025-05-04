from django.contrib import admin
from chess_models.models import Tournament, Player, Game, Round, Referee

# Configuración avanzada para Torneos
class TournamentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'location')
    list_filter = ('start_date', 'end_date')
    ordering = ('start_date',)
    date_hierarchy = 'start_date'
    list_per_page = 10
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        # Implementar la lógica para exportar a CSV
        pass

    export_as_csv.short_description = "Export selected tournaments as CSV"

# Registro de modelos
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Round)
admin.site.register(Referee)