from django.apps import AppConfig


class TradeConfig(AppConfig):
    name = 'trades'

    def ready(self):
        import trades.signals
