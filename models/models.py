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

    _logger.info("WSEM VariantGridWizard")
    attribute_serie_id = fields.Many2one('attribute.serie', string="Serie de Atributos")
    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Línea de Pedido de Compra")
    # Asumiendo que `attribute.serie` es tu modelo de serie de atributos
    # y que contiene referencias a las tallas (p.ej., mediante un campo One2many hacia `attribute.serie.item`)
    
    line_ids = fields.One2many('variant.grid.wizard.line', 'wizard_id', string="Líneas")
    
    talla_1_nombre = fields.Char("Talla 1 Nombre", default="T1")
    talla_2_nombre = fields.Char("Talla 2 Nombre", default="T2")
    talla_3_nombre = fields.Char("Talla 3 Nombre", default="T3")
    
    @api.model
    def default_get(self, fields_list):
        res = super(VariantGridWizard, self).default_get(fields_list)
        # Buscar todos los valores de atributo de color disponibles
        color_attribute_values = self.env['product.attribute.value'].search([('attribute_id.name', '=', 'Color')])

        line_vals = []
        for color_value in color_attribute_values:
            # Para cada color, crear una línea con las cantidades inicializadas a nulo (o cero)
            line_vals.append((0, 0, {
                'color_id': color_value.id,
                'talla_1': 0,  # o `False` si prefieres inicializar como nulo
                'talla_2': 0,  # o `False`
                'talla_3': 0,  # o `False`
            }))
        
        res['line_ids'] = line_vals
        return res


    

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        _logger.info("WSEM onchange_attribute_serie")
        # Si no hay serie seleccionada, dejar los nombres de tallas en blanco
        if not self.attribute_serie_id:
            self.talla_1_nombre = ""
            self.talla_2_nombre = ""
            self.talla_3_nombre = ""
            for line in self.line_ids:
                line.talla_1 = False  # Asumiendo que quieras limpiar las cantidades también
                line.talla_2 = False
                line.talla_3 = False
            return

        # Obtener los nombres de las tallas de la serie seleccionada
        tallas = self.attribute_serie_id.item_ids.mapped('attribute_value_id')
        nombres_tallas = [talla.name for talla in tallas]

        # Actualizar los nombres de las tallas
        self.talla_1_nombre = nombres_tallas[0] if len(nombres_tallas) > 0 else ""
        self.talla_2_nombre = nombres_tallas[1] if len(nombres_tallas) > 1 else ""
        self.talla_3_nombre = nombres_tallas[2] if len(nombres_tallas) > 2 else ""
        
        
        if self.talla_1_nombre:
            _logger.info(f"WSEM talla 1 {self.talla_1_nombre}")
            for line in self.line_ids:
                line.talla_1 = self.talla_1_nombre
        # Si una talla no está presente, sus cantidades en las líneas deberían ser limpiadas
        if not self.talla_2_nombre:
            for line in self.line_ids:
                line.talla_2 = False
        if not self.talla_3_nombre:
            for line in self.line_ids:
                line.talla_3 = False


                    
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
                        cantidad = getattr(detail, f'{talla}', 0)
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