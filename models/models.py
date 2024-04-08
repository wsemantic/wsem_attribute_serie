from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

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


class VariantGridWizard(models.TransientModel):
    _name = 'variant.grid.wizard'
    _description = 'Wizard para Cuadrícula de Variantes'

    attribute_serie_id = fields.Many2one('attribute.serie', string="Serie de Atributos")
    # Asumiendo que `attribute.serie` es tu modelo de serie de atributos
    # y que contiene referencias a las tallas (p.ej., mediante un campo One2many hacia `attribute.serie.item`)
    
    line_ids = fields.One2many('variant.grid.wizard.line', 'wizard_id', string="Líneas")

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        # Limpiar las líneas existentes
        self.line_ids = [(5, 0, 0)]
        # Asumiendo que tu modelo de serie de atributos tiene acceso a los colores y sus tallas
        if self.attribute_serie_id:
            # Aquí deberías implementar la lógica para poblar `line_ids` basado en la serie seleccionada
            # Esto es un ejemplo simplificado
            for color in self.env['product.attribute.value'].search([]): # Esto es solo un placeholder, ajusta según tu modelo de datos
                self.line_ids.create({
                    'color_id': color.id,
                    'wizard_id': self.id,
                    'talla_1': 'Talla 1', # Estos valores deben ser dinámicos basados en la serie
                    'talla_2': 'Talla 2',
                    'talla_3': 'Talla 3',
                    # Asumiendo que deseas inicializar las cantidades en cero o algún valor predeterminado
                    'cantidad_talla_1': 0,
                    'cantidad_talla_2': 0,
                    'cantidad_talla_3': 0,
                })
    def button_accept(self):
        # Crear las líneas de variantes según las cantidades ingresadas
        if self.purchase_order_line_id:
            variant_grid = {
                'tallas': [detail.talla_1 for detail in self.detail_ids if detail.talla_1],
                'colores': [detail.color_id.name for detail in self.detail_ids if detail.color_id],
            }
            for detail in self.detail_ids:
                if detail.color_id:
                    for talla in variant_grid['tallas']:
                        cantidad = getattr(detail, f'{talla}_cantidad', 0)
                        if cantidad > 0:
                            variant_grid[f'{talla}_{detail.color_id.name}'] = cantidad

            # Llamar al método create_variant_lines en la línea de pedido de compra
            self.purchase_order_line_id.with_context(variant_grid=variant_grid).create_variant_lines()

        # Devolver la acción de cierre de la ventana emergente
            return {'type': 'ir.actions.act_window_close'}

class VariantGridWizardLine(models.TransientModel):
    _name = 'variant.grid.wizard.line'
    _description = 'Línea de Wizard para Cuadrícula de Variantes'

    wizard_id = fields.Many2one('variant.grid.wizard', string="Wizard de Variantes", required=True, ondelete='cascade')
    color_id = fields.Many2one('product.attribute.value', string="Color", required=True)
    talla_1 = fields.Char("Talla 1")
    talla_2 = fields.Char("Talla 2")
    talla_3 = fields.Char("Talla 3")
    cantidad_talla_1 = fields.Integer("Cantidad Talla 1")
    cantidad_talla_2 = fields.Integer("Cantidad Talla 2")
    cantidad_talla_3 = fields.Integer("Cantidad Talla 3")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

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