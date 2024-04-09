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
    
    nombres_tallas = fields.Text(string='Nombres de Tallas', default='["T1", "T2", "T3"]')
    
    @api.model
    def default_get(self, fields_list):
        res = super(VariantGridWizard, self).default_get(fields_list)
        # Inicializar la "fila de encabezado" con valores predeterminados para las tallas
        res['line_ids'] = [(0, 0, {'color_id': False, 'talla_1': 'Talla 1', 'talla_2': 'Talla 2', 'talla_3': 'Talla 3'})]
        return res


    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        if self.attribute_serie_id:
            # Obtener los nombres de las tallas de la serie seleccionada
            tallas = self.attribute_serie_id.item_ids.mapped('attribute_value_id')
            nombres_tallas = [talla.name for talla in tallas][:3]

            # Asegurarse de que hay al menos 3 nombres (rellenar con vacío si es necesario)

            # Convertir la lista de nombres a un string JSON válido
            nombres_tallas_json = json.dumps(nombres_tallas)
            _logger.info(f"WSEM talla 1 {nombres_tallas_json}")

            # Actualizar el campo con el string JSON
            self.nombres_tallas = nombres_tallas_json

            # Actualizar la fila de encabezado (asumiendo que siempre es la primera línea)
            if self.line_ids:
                self.line_ids[0].talla_1 = nombres_tallas[0]
                self.line_ids[0].talla_2 = nombres_tallas[1]
                self.line_ids[0].talla_3 = nombres_tallas[2]
        else:
            # Si no hay serie seleccionada, reiniciar a los valores predeterminados
            self.nombres_tallas = '["Talla 1", "Talla 2", "Talla 3"]'



                    
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
    color_id = fields.Many2one(
        'product.attribute.value',
        string='Color',
        domain="[('attribute_id.name', '=', 'Color')]"
    )
    
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