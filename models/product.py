# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Serie Tallas')  

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        if self.attribute_serie_id:
            attribute_id = self.env['product.attribute'].search([('name', '=', 'Talla')], limit=1)
            if attribute_id:
                existing_line = self.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute_id)

                # Get attribute values sorted by sequence and name
                sorted_attribute_values = self.attribute_serie_id.item_ids.sorted(
                    key=lambda item: (item.sequence or 0, item.attribute_value_id.name)
                )
                attribute_value_ids = sorted_attribute_values.mapped('attribute_value_id').ids

                if existing_line:
                    _logger.info("WSEM existed as a series line")
                    existing_line.value_ids = [(6, 0, attribute_value_ids)]
                else:
                    _logger.info("WSEM creating series")
                    self.attribute_line_ids = [(0, 0, {
                        'attribute_id': attribute_id.id,
                        'value_ids': [(6, 0, attribute_value_ids)]
                    })]

    @staticmethod
    def _is_purchase_context(env):
        # The custom checks only apply when the product is being managed from a
        # purchase order / line. Any other write path (UI product form, imports,
        # the migrator, POS, ...) is left untouched.
        ctx = env.context
        if ctx.get('active_model') in {'purchase.order', 'purchase.order.line'}:
            return True
        # "Crear y editar" un producto desde la línea de compra NO trae
        # active_model, pero sí marcadores del origen compra: 'quotation_only'
        # (lo pone el contexto del campo product en purchase) y/o la acción web
        # 'purchase' en params. Con esto la constraint (serie/color/proveedor/
        # precio) vuelve a exigirse al crear la plantilla desde una compra.
        if ctx.get('quotation_only'):
            return True
        params = ctx.get('params') or {}
        if params.get('action') == 'purchase':
            return True
        return False

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # v18: "bien" (type='consu') ya es el default del core. Ofrecemos
        # is_storable marcado por defecto en el formulario nuevo de un bien, para
        # que el usuario lo vea marcado (puede desmarcarlo). No basta con
        # setdefault en create(): la UI envía is_storable=False explícito (default
        # del core), y ahí un setdefault no pisaría nada. is_storable es
        # compute-stored @api.depends('type'): el core lo fuerza a False en
        # service/combo, así que en consu el True persiste; no se toca 'type' ni
        # el difunto 'detailed_type' de v16.
        if 'is_storable' in fields_list and res.get('type', 'consu') == 'consu':
            res['is_storable'] = True
        # Al crear el producto desde una línea de compra, el contexto trae el
        # proveedor del pedido ('partner_id'); pre-rellenamos una línea de
        # proveedor con él para no tener que seleccionarlo (solo falta teclear el
        # precio, que la constraint exige > 0). Solo en contexto de compra.
        if 'seller_ids' in fields_list and not res.get('seller_ids') \
                and self._is_purchase_context(self.env):
            partner_id = self.env.context.get('partner_id')
            if partner_id:
                res['seller_ids'] = [(0, 0, {'partner_id': partner_id})]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Respaldo para creaciones por ORM que no pasan por default_get y omiten
        # is_storable (bien almacenable por defecto). Se hace en este create (el
        # externo, ya que este módulo depende de wsem_pos) para que wsem_pos lo
        # lea y aplique available_in_pos.
        for vals in vals_list:
            if vals.get('type', 'consu') == 'consu':
                vals.setdefault('is_storable', True)
        products = super().create(vals_list)
        # Precio de venta obligatorio en almacenables SOLO en contexto de compra
        # (junto al resto de reglas de _check_custom_fields). Detecta un precio
        # olvidado: si 'list_price' no viajó en vals el core aplicó su default
        # (1.0); un valor provisto -- aunque sea 0 o 1 -- se considera editado y
        # pasa (el migrador e importaciones siempre lo envían explícito). Vive en
        # create() (no en la constraint) porque solo aquí se distingue un 1.0
        # tecleado del 1.0 por defecto.
        if self._is_purchase_context(self.env):
            for vals, product in zip(vals_list, products):
                if product.is_storable and 'list_price' not in vals:
                    raise ValidationError(_(
                        "Para los productos almacenables creados desde pedidos de compra debe indicarse el precio de venta."
                    ))
        return products

    @api.constrains('is_storable', 'type', 'attribute_serie_id', 'seller_ids', 'attribute_line_ids')
    def _check_custom_fields(self):
        has_defined_series = bool(self.env['attribute.serie'].search_count([], limit=1))
        is_purchase_context = self._is_purchase_context(self.env)

        for product in self:
            if product.is_storable:  # Only for storable products (in v18, is_storable replaces type == 'product')
                # Series, vendors and color are only required when the storable
                # product is managed from purchase orders or their lines. Outside
                # a purchase context (UI/POS/quick-create) a storable product may
                # be created without a series, so defaulting is_storable=True does
                # not block normal product creation.
                if is_purchase_context:
                    # Only require a series if at least one attribute.serie exists.
                    if has_defined_series and not product.attribute_serie_id:
                        raise ValidationError(_(
                            "Para los productos almacenables creados desde pedidos de compra, el campo 'Serie de atributos' es obligatorio cuando existen series definidas."
                        ))
                    if not product.seller_ids:
                        raise ValidationError(_(
                            "Para los productos almacenables creados desde pedidos de compra debe existir al menos un proveedor."
                        ))
                    if not any(s.price > 0 for s in product.seller_ids):
                        raise ValidationError(_(
                            "Para los productos almacenables creados desde pedidos de compra, al menos un proveedor debe tener precio de compra mayor que cero."
                        ))

                    color_lines = product.attribute_line_ids.filtered(lambda l: l.attribute_id.name.lower() == 'color')
                    if not color_lines or not any(line.value_ids for line in color_lines):
                        raise ValidationError(_("Debe agregarse al menos un valor para el atributo 'Color' en el producto."))
