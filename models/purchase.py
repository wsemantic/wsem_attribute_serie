from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('order_line')
    def _onchange_propagate_price_unit(self):
        # For each product.template present in the lines, we check if any line has a price assigned and propagate it to the others.
        for tmpl in self.order_line.mapped('product_id.product_tmpl_id'):
            # Filter lines that belong to this product.template
            lines = self.order_line.filtered(lambda l: l.product_id.product_tmpl_id == tmpl)
            # Search for a defined price (different from 0) in any of the lines
            defined_price = next((l.price_unit for l in lines if l.price_unit and l.price_unit != 0), False)
            if defined_price:
                for line in lines:
                    if not line.price_unit or line.price_unit == 0:
                        _logger.info(f"Propagando precio {defined_price} en línea {line.id if line.id else 'nueva'}")
                        line.price_unit = defined_price
        return {}

    
    