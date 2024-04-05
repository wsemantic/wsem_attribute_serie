from odoo import models, fields, api

class AttributeSerie(models.Model):
    _name = 'attribute.serie'
    _description = 'Attribute Serie'

    name = fields.Char(string='Name', required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie')
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', related='product_id.attribute_serie_id', readonly=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.attribute_serie_id = self.product_id.attribute_serie_id
            self.create_variant_grid()

    @api.onchange('product_id')
    def create_variant_grid(self):
        if self.product_id and self.attribute_serie_id:
            # Obtener las tallas de la serie del producto
            tallas = self.attribute_serie_id.talla_ids.mapped('name')

            # Obtener todos los colores posibles para el producto
            colores = self.product_id.attribute_line_ids.filtered(lambda x: x.attribute_id.name == 'Color').value_ids.mapped('name')

            # Crear el XML dinámicamente para la cuadrícula de variantes
            xml = """
            <form>
                <group>
                    <field name="product_id" readonly="1"/>
                    <field name="order_id" readonly="1"/>
                </group>
                <group>
                    <table class="variant_grid">
                        <thead>
                            <tr>
                                <th></th>
                                """ + ''.join(['<th>%s</th>' % talla for talla in tallas]) + """
                            </tr>
                        </thead>
                        <tbody>
                            """ + ''.join(['<tr><td>%s</td>%s</tr>' % (color, ''.join(['<td><field name="%s_%s"/></td>' % (talla, color) for talla in tallas])) for color in colores]) + """
                        </tbody>
                    </table>
                </group>
                <footer>
                    <button name="create_variant_lines" type="object" string="Aceptar" class="btn-primary"/>
                    <button string="Cancelar" class="btn-default" special="cancel"/>
                </footer>
            </form>
            """

            # Crear la ventana emergente con la cuadrícula de variantes
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cuadrícula de Variantes',
                'res_model': 'purchase.order.line',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': {
                    'default_product_id': self.product_id.id,
                    'default_order_id': self.order_id.id,
                    'default_attribute_serie_id': self.attribute_serie_id.id,
                    'tallas': tallas,
                    'colores': colores,
                },
                'arch': xml,
            }
    
    
    @api.multi
    def create_variant_lines(self):
        self.ensure_one()
        variant_grid = self.read()[0]

        for talla in variant_grid['tallas']:
            for color in variant_grid['colores']:
                cantidad = variant_grid.get('%s_%s' % (talla, color), 0)
                if cantidad > 0:
                    variante = self.product_id.product_variant_ids.filtered(lambda x: x.attribute_value_ids.filtered(lambda y: y.name == talla) and x.attribute_value_ids.filtered(lambda y: y.name == color))
                    if variante:
                        self.create({
                            'product_id': variante.id,
                            'product_qty': cantidad,
                            'order_id': self.order_id.id,
                        })

        return {'type': 'ir.actions.act_window_close'}