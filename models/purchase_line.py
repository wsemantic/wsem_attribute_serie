from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('price_unit')
    def _onchange_price_unit_propagate(self):
        _logger.info(f"WSEM compras cambio precio")
        # Se ejecuta cuando se asigna un precio distinto de 0
        if self.product_id and self.price_unit and self.price_unit != 0:
            _logger.info(f"WSEM existe precio")
            # Filtra las líneas del mismo pedido que:
            #  - Pertenecen al mismo product.template (es decir, son variantes del mismo producto)
            #  - Tienen price_unit igual a 0 (no han sido modificadas)
            #  - Aún no han sido persistidas en la base de datos (line.id es False)
            similar_lines = self.order_id.order_line.filtered(
                lambda line: line.product_id.product_tmpl_id == self.product_id.product_tmpl_id and
                             (not line.price_unit or line.price_unit == 0)
            )
            if similar_lines:
                _logger.info(f"WSEM linea similar")
                similar_lines.price_unit = self.price_unit
