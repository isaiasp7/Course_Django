from django.contrib import admin

from .models import Agenda, AgendaServico, Servicos


class AgendaServicoInline(admin.TabularInline):
    model = AgendaServico
    extra = 0


@admin.register(Servicos)
class ServicosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'preco')
    search_fields = ('nome',)


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'hora', 'clienteFk', 'profissionalFk')
    list_filter = ('data', 'profissionalFk')
    inlines = [AgendaServicoInline]


@admin.register(AgendaServico)
class AgendaServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'agenda_id', 'servico_id', 'agenda', 'servico')
    list_filter = ('servico',)
