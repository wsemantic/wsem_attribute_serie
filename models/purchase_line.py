from odoo import models, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_set_supplier_price(self):
        """Si se asigna un producto y éste tiene un coste definido,
        se comprueba si ya existe un precio de compra para el proveedor del pedido.
        En caso negativo, se crea uno usando el coste del producto."""
        if self.product_id and self.order_id.partner_id:
            supplier = self.order_id.partner_id
            cost = self.product_id.standard_price
            if cost:
                # Se trabaja sobre el product.template del producto, ya que allí se gestionan los supplierinfo.
                tmpl = self.product_id.product_tmpl_id
                # Filtramos los registros existentes para este proveedor.
                supplier_info = tmpl.seller_ids.filtered(lambda s: s.name.id == supplier.id)
                if not supplier_info:
                    tmpl.seller_ids = [(0, 0, {
                        'name': supplier.id,
                        'price': cost,
                        # Puedes agregar otros campos por defecto, como 'min_qty', 'delay', etc.
                    })]
