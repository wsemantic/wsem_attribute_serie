from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.onchange('price_unit')
    def _onchange_price_unit_propagate(self):
        _logger.info("WSEM compras cambio precio")
        if self.product_id and self.price_unit and self.price_unit != 0:
            _logger.info("WSEM existe precio")
            # Generamos la lista de comandos para actualizar las líneas
            new_lines = []
            for line in self.order_id.order_line:
                # Si la línea corresponde al mismo product.template y el precio es 0
                if line.product_id.product_tmpl_id == self.product_id.product_tmpl_id and (not line.price_unit or line.price_unit == 0):
                    if line.id:
                        # Para líneas ya persistidas: usamos el comando (1, id, values)
                        new_lines.append((1, line.id, {'price_unit': self.price_unit}))
                    else:
                        # Para líneas nuevas (no persistidas): modificamos la caché directamente
                        line.price_unit = self.price_unit
                        # Es importante conservar la estructura del valor de order_line:
                        # (0, 0, {vals}) para nuevas líneas
                        new_lines.append((0, 0, line._convert_to_write({})))
                else:
                    # Para las líneas que no se actualizan, se conservan sin cambios
                    # (Si la línea ya está en la caché, se la incluye usando el comando adecuado)
                    if line.id:
                        new_lines.append((1, line.id, {}))
                    else:
                        new_lines.append((0, 0, line._convert_to_write({})))
                        
            return {'value': {'order_line': new_lines}}
    
    