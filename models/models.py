from odoo import models, fields, api

class AttributeSerie(models.Model):
    _name = 'attribute.serie'
    _description = 'Attribute Serie'

    name = fields.Char(string='Name', required=True)
    item_ids = fields.One2many('attribute.serie.item', 'attribute_serie_id', string='Items')

class AttributeSerieItem(models.Model):
    _name = 'attribute.serie.item'
    _description = 'Attribute Serie Item'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', required=True, ondelete='cascade')
    attribute_value_id = fields.Many2one('product.attribute.value', string='Attribute Value', required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie')
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', related='product_id.attribute_serie_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.attribute_serie_id = self.product_id.attribute_serie_id
            self.create_variant_grid()

    @api.onchange('product_id')
    def create_variant_grid(self):
        if self.product_id and self.attribute_serie_id:
            # Obtener los valores de atributo de la serie seleccionada
            attribute_values = self.attribute_serie_id.item_ids.mapped('attribute_value_id')

            # Obtener las tallas de la serie seleccionada
            tallas = attribute_values.filtered(lambda x: x.attribute_id.name == 'Talla').mapped('name')

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
    
    
    def create_variant_lines(self):
        variant_grid = self.env.context.get('variant_grid', {})

        for talla in variant_grid.get('tallas', []):
            for color in variant_grid.get('colores', []):
                cantidad = variant_grid.get(f'{talla}_{color}', 0)
                if cantidad > 0:
                    variante = self.product_id.product_variant_ids.filtered(lambda x: 
                        x.attribute_value_ids.filtered(lambda y: y.name == talla) and 
                        x.attribute_value_ids.filtered(lambda y: y.name == color))
                    if variante:
                        self.env['purchase.order.line'].create({
                            'product_id': variante.id,
                            'product_qty': cantidad,
                            'order_id': self.order_id.id,
                        })

        return {'type': 'ir.actions.act_window_close'}