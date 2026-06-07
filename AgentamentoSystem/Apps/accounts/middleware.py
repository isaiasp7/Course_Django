from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from .models import TipoUsuario

SESSION_NAV_TOKEN = 'guest_nav_token'
SESSION_AUTHORIZED_PATH = 'guest_authorized_path'

GUEST_PATHS = frozenset({
    '/accounts/cadastro/',
    '/accounts/profissional/codigo/',
})


def build_guest_url(view_name, token):
    if not token:
        return reverse(view_name)
    return f'{reverse(view_name)}?nav={token}'


def deny_access(request):
    if request.method != 'GET':
        return JsonResponse(
            {'success': False, 'error': 'Faca login para continuar.'},
            status=401,
        )
    return redirect(reverse('accounts:login'))


class RouteProtectionMiddleware:
    """Bloqueia acesso direto por URL fora do fluxo iniciado no login."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith('/static/') or path.startswith('/admin/'):
            return self.get_response(request)

        if path == reverse('accounts:login'):
            return self.get_response(request)

        if path in GUEST_PATHS:
            return self._handle_guest_path(request, path)

        if self._requires_authentication(path):
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                return deny_access(request)

            usuario_tipo = request.session.get('usuario_tipo')
            if path.startswith('/dashboard/profissional/'):
                if usuario_tipo != TipoUsuario.PROFISSIONAL:
                    return deny_access(request)
            elif path.startswith('/appointments/'):
                if usuario_tipo != TipoUsuario.CLIENTE:
                    return deny_access(request)
            elif path.startswith('/dashboard/'):
                if usuario_tipo != TipoUsuario.CLIENTE:
                    return deny_access(request)

        return self.get_response(request)

    def _handle_guest_path(self, request, path):
        session_token = request.session.get(SESSION_NAV_TOKEN)

        if request.method == 'GET':
            nav = request.GET.get('nav', '')
            if not session_token or nav != session_token:
                return deny_access(request)
            request.session[SESSION_AUTHORIZED_PATH] = path
        elif request.session.get(SESSION_AUTHORIZED_PATH) != path:
            return deny_access(request)

        return self.get_response(request)

    @staticmethod
    def _requires_authentication(path):
        return (
            path.startswith('/dashboard/')
            or path.startswith('/appointments/')
            or path.startswith('/accounts/perfil/')
        )
