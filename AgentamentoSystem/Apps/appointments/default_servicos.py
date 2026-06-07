from decimal import Decimal

SERVICOS_PADRAO = [
    ('Corte Masculino', Decimal('45.00')),
    ('Corte Infantil', Decimal('40.00')),
    ('Escova', Decimal('50.00')),
    ('Escova Progressiva', Decimal('120.00')),
    ('Selagem', Decimal('150.00')),
    ('Coloração', Decimal('90.00')),
    ('Mechas', Decimal('130.00')),
    ('Luzes', Decimal('140.00')),
    ('Botox Capilar', Decimal('110.00')),
    ('Hidratação', Decimal('60.00')),
    ('Reconstrução Capilar', Decimal('80.00')),
    ('Penteado para Festa', Decimal('100.00')),
    ('Tranças', Decimal('70.00')),
    ('Relaxamento', Decimal('95.00')),
    ('Alisamento', Decimal('180.00')),
    ('Finalização', Decimal('35.00')),
    ('Tratamento Anti-Queda', Decimal('85.00')),
    ('Corte e Escova', Decimal('95.00')),
    ('Sobrancelha (Design)', Decimal('30.00')),
]


def ensure_default_servicos():
    from .models import Servicos

    for nome, preco in SERVICOS_PADRAO:
        Servicos.objects.get_or_create(
            nome=nome,
            defaults={'preco': preco},
        )
